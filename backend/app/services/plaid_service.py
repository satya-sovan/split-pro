"""
Plaid service for bank account integration
Handles connecting accounts and fetching transactions
"""
from typing import List, Optional, Dict
from datetime import datetime, timedelta
import plaid
from plaid.api import plaid_api
from plaid.model.products import Products
from plaid.model.country_code import CountryCode
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.link_token_create_request_user import LinkTokenCreateRequestUser
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.transactions_get_request import TransactionsGetRequest
from plaid.model.transactions_get_request_options import TransactionsGetRequestOptions
from sqlalchemy.orm import Session

from app.core.config import settings
from app.models.models import User, CachedBankData


class PlaidService:
    """Service for Plaid bank integration"""

    def __init__(self):
        configuration = plaid.Configuration(
            host=self._get_plaid_host(),
            api_key={
                'clientId': settings.PLAID_CLIENT_ID,
                'secret': settings.PLAID_SECRET,
            }
        )
        api_client = plaid.ApiClient(configuration)
        self.client = plaid_api.PlaidApi(api_client)

    def _get_plaid_host(self) -> str:
        """Get Plaid API host based on environment"""
        env_map = {
            'sandbox': plaid.Environment.Sandbox,
            'development': plaid.Environment.Development,
            'production': plaid.Environment.Production
        }
        return env_map.get(settings.PLAID_ENV, plaid.Environment.Sandbox)

    async def create_link_token(
        self,
        user_id: int,
        user_name: str,
        language: str = 'en'
    ) -> Dict[str, str]:
        """
        Create a Link token for Plaid Link initialization

        Args:
            user_id: User ID
            user_name: User's name
            language: User's preferred language

        Returns:
            Dictionary with link_token and expiration
        """
        try:
            request = LinkTokenCreateRequest(
                user=LinkTokenCreateRequestUser(client_user_id=str(user_id)),
                client_name="SAHASplit",
                products=[Products("transactions")],
                country_codes=[CountryCode('US'), CountryCode('GB'), CountryCode('CA')],
                language=language,
                redirect_uri=f"{settings.CORS_ORIGINS[0]}/bank/oauth-redirect"
            )

            response = self.client.link_token_create(request)

            return {
                'link_token': response['link_token'],
                'expiration': response['expiration']
            }

        except plaid.ApiException as e:
            print(f"Error creating link token: {e}")
            raise ValueError(f"Failed to create link token: {e}")

    async def exchange_public_token(
        self,
        public_token: str,
        db: Session,
        user_id: int
    ) -> Dict[str, str]:
        """
        Exchange public token for access token

        Args:
            public_token: Public token from Plaid Link
            db: Database session
            user_id: User ID

        Returns:
            Dictionary with access_token and item_id
        """
        try:
            request = ItemPublicTokenExchangeRequest(public_token=public_token)
            response = self.client.item_public_token_exchange(request)

            access_token = response['access_token']
            item_id = response['item_id']

            # Store access token in user record
            user = db.query(User).filter(User.id == user_id).first()
            if user:
                user.obapi_provider_id = access_token
                user.banking_id = item_id
                db.commit()

            return {
                'access_token': access_token,
                'item_id': item_id
            }

        except plaid.ApiException as e:
            print(f"Error exchanging token: {e}")
            raise ValueError(f"Failed to exchange token: {e}")

    async def get_transactions(
        self,
        access_token: str,
        start_date: datetime,
        end_date: datetime,
        db: Session,
        user_id: int
    ) -> List[Dict]:
        """
        Fetch transactions from Plaid

        Args:
            access_token: Plaid access token
            start_date: Start date for transactions
            end_date: End date for transactions
            db: Database session
            user_id: User ID for caching

        Returns:
            List of transaction dictionaries
        """
        try:
            request = TransactionsGetRequest(
                access_token=access_token,
                start_date=start_date.date(),
                end_date=end_date.date(),
                options=TransactionsGetRequestOptions(
                    count=500,
                    offset=0
                )
            )

            response = self.client.transactions_get(request)
            transactions = response['transactions']

            # Pagination if needed
            while len(transactions) < response['total_transactions']:
                request.options.offset = len(transactions)
                response = self.client.transactions_get(request)
                transactions.extend(response['transactions'])

            # Cache transactions
            await self._cache_transactions(db, user_id, transactions)

            # Convert to dict format
            return [self._transaction_to_dict(t) for t in transactions]

        except plaid.ApiException as e:
            print(f"Error fetching transactions: {e}")
            raise ValueError(f"Failed to fetch transactions: {e}")

    async def _cache_transactions(
        self,
        db: Session,
        user_id: int,
        transactions: List
    ):
        """Cache transactions in database"""
        import json

        for transaction in transactions:
            transaction_id = transaction.get('transaction_id')

            # Check if already cached
            existing = db.query(CachedBankData).filter(
                CachedBankData.user_id == user_id,
                CachedBankData.transaction_id == transaction_id
            ).first()

            if not existing:
                cached = CachedBankData(
                    user_id=user_id,
                    transaction_id=transaction_id,
                    provider='plaid',
                    data=json.dumps(self._transaction_to_dict(transaction)),
                    cached_at=datetime.utcnow()
                )
                db.add(cached)

        db.commit()

    def _transaction_to_dict(self, transaction) -> Dict:
        """Convert Plaid transaction to dictionary"""
        return {
            'transaction_id': transaction.get('transaction_id'),
            'account_id': transaction.get('account_id'),
            'amount': float(transaction.get('amount', 0)),
            'date': str(transaction.get('date')),
            'name': transaction.get('name'),
            'merchant_name': transaction.get('merchant_name'),
            'category': transaction.get('category', []),
            'pending': transaction.get('pending', False),
            'currency': transaction.get('iso_currency_code', 'USD'),
            'payment_channel': transaction.get('payment_channel')
        }

    async def get_institutions(self, country_code: str = 'US') -> List[Dict]:
        """
        Get list of supported institutions

        Args:
            country_code: Country code (US, GB, CA, etc.)

        Returns:
            List of institution dictionaries
        """
        # This is a simplified version - in production, you'd want to
        # use Plaid's institutions/search endpoint
        return [
            {
                'institution_id': 'ins_1',
                'name': 'Chase',
                'country': country_code,
                'logo': None
            },
            {
                'institution_id': 'ins_2',
                'name': 'Bank of America',
                'country': country_code,
                'logo': None
            },
            {
                'institution_id': 'ins_3',
                'name': 'Wells Fargo',
                'country': country_code,
                'logo': None
            }
        ]


# Global service instance
plaid_service = PlaidService() if settings.PLAID_CLIENT_ID else None

