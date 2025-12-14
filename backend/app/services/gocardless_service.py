"""
GoCardless (Nordigen) service for bank account integration
Handles Open Banking API for European banks
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import httpx
from sqlalchemy.orm import Session
import json

from app.core.config import settings
from app.models.models import User, CachedBankData


class GoCardlessService:
    """Service for GoCardless/Nordigen bank integration"""

    def __init__(self):
        self.base_url = "https://bankaccountdata.gocardless.com/api/v2"
        self.secret_id = settings.GOCARDLESS_SECRET_ID
        self.secret_key = settings.GOCARDLESS_SECRET_KEY
        self.access_token = None
        self.token_expires = None

    async def _get_access_token(self) -> str:
        """Get or refresh access token"""
        # Check if we have a valid token
        if self.access_token and self.token_expires:
            if datetime.utcnow() < self.token_expires:
                return self.access_token

        # Get new token
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/token/new/",
                json={
                    "secret_id": self.secret_id,
                    "secret_key": self.secret_key
                }
            )

            if response.status_code == 200:
                data = response.json()
                self.access_token = data['access']
                # Token expires in ~30 days, refresh before that
                self.token_expires = datetime.utcnow() + timedelta(days=29)
                return self.access_token
            else:
                raise ValueError(f"Failed to get access token: {response.text}")

    async def get_institutions(
        self,
        country_code: str = 'GB'
    ) -> List[Dict]:
        """
        Get list of supported institutions for a country

        Args:
            country_code: ISO 3166 country code (GB, DE, FR, etc.)

        Returns:
            List of institution dictionaries
        """
        token = await self._get_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/institutions/",
                params={"country": country_code},
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 200:
                institutions = response.json()
                return [
                    {
                        'institution_id': inst['id'],
                        'name': inst['name'],
                        'country': country_code,
                        'logo': inst.get('logo'),
                        'bic': inst.get('bic')
                    }
                    for inst in institutions
                ]
            else:
                print(f"Error fetching institutions: {response.text}")
                return []

    async def create_requisition(
        self,
        institution_id: str,
        user_id: int,
        language: str = 'en'
    ) -> Dict[str, str]:
        """
        Create a requisition (connection) to a bank

        Args:
            institution_id: Institution ID from get_institutions
            user_id: User ID
            language: User's preferred language

        Returns:
            Dictionary with link (redirect URL) and requisition_id
        """
        token = await self._get_access_token()

        redirect_uri = f"{settings.CORS_ORIGINS[0]}/bank/callback"

        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/requisitions/",
                headers={"Authorization": f"Bearer {token}"},
                json={
                    "redirect": redirect_uri,
                    "institution_id": institution_id,
                    "reference": f"user_{user_id}",
                    "user_language": language.upper()
                }
            )

            if response.status_code in [200, 201]:
                data = response.json()
                return {
                    'link': data['link'],
                    'requisition_id': data['id']
                }
            else:
                raise ValueError(f"Failed to create requisition: {response.text}")

    async def get_accounts(
        self,
        requisition_id: str
    ) -> List[str]:
        """
        Get account IDs from a requisition

        Args:
            requisition_id: Requisition ID

        Returns:
            List of account IDs
        """
        token = await self._get_access_token()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/requisitions/{requisition_id}/",
                headers={"Authorization": f"Bearer {token}"}
            )

            if response.status_code == 200:
                data = response.json()
                return data.get('accounts', [])
            else:
                print(f"Error fetching accounts: {response.text}")
                return []

    async def get_transactions(
        self,
        account_id: str,
        db: Session,
        user_id: int,
        date_from: Optional[datetime] = None,
        date_to: Optional[datetime] = None
    ) -> List[Dict]:
        """
        Fetch transactions from an account

        Args:
            account_id: Account ID
            db: Database session
            user_id: User ID for caching
            date_from: Start date (default: 90 days ago)
            date_to: End date (default: today)

        Returns:
            List of transaction dictionaries
        """
        token = await self._get_access_token()

        if not date_from:
            date_from = datetime.utcnow() - timedelta(days=90)
        if not date_to:
            date_to = datetime.utcnow()

        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{self.base_url}/accounts/{account_id}/transactions/",
                headers={"Authorization": f"Bearer {token}"},
                params={
                    "date_from": date_from.strftime("%Y-%m-%d"),
                    "date_to": date_to.strftime("%Y-%m-%d")
                }
            )

            if response.status_code == 200:
                data = response.json()
                transactions = data.get('transactions', {}).get('booked', [])

                # Cache transactions
                await self._cache_transactions(db, user_id, account_id, transactions)

                return [self._transaction_to_dict(t) for t in transactions]
            else:
                print(f"Error fetching transactions: {response.text}")
                return []

    async def _cache_transactions(
        self,
        db: Session,
        user_id: int,
        account_id: str,
        transactions: List[Dict]
    ):
        """Cache transactions in database"""
        for transaction in transactions:
            transaction_id = transaction.get('transactionId') or transaction.get('internalTransactionId')

            if not transaction_id:
                continue

            # Check if already cached
            existing = db.query(CachedBankData).filter(
                CachedBankData.user_id == user_id,
                CachedBankData.transaction_id == transaction_id
            ).first()

            if not existing:
                cached = CachedBankData(
                    user_id=user_id,
                    transaction_id=transaction_id,
                    provider='gocardless',
                    account_id=account_id,
                    data=json.dumps(self._transaction_to_dict(transaction)),
                    cached_at=datetime.utcnow()
                )
                db.add(cached)

        db.commit()

    def _transaction_to_dict(self, transaction: Dict) -> Dict:
        """Convert GoCardless transaction to standardized dictionary"""
        amount_data = transaction.get('transactionAmount', {})

        return {
            'transaction_id': transaction.get('transactionId') or transaction.get('internalTransactionId'),
            'account_id': transaction.get('accountId'),
            'amount': float(amount_data.get('amount', 0)),
            'currency': amount_data.get('currency', 'EUR'),
            'date': transaction.get('bookingDate') or transaction.get('valueDate'),
            'name': transaction.get('remittanceInformationUnstructured', ''),
            'merchant_name': transaction.get('creditorName') or transaction.get('debtorName'),
            'category': [],
            'pending': False,
            'payment_channel': 'bank_transfer',
            'creditor_account': transaction.get('creditorAccount'),
            'debtor_account': transaction.get('debtorAccount')
        }


# Global service instance
gocardless_service = GoCardlessService() if settings.GOCARDLESS_SECRET_ID else None

