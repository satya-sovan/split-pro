-- SQL Migration: Add notification_preferences and created_at columns to users table
-- Run this if Alembic migrations fail or need to be done manually

-- Add notification_preferences column (JSON type)
ALTER TABLE users ADD COLUMN notification_preferences JSON NULL;

-- Add created_at column with default timestamp
ALTER TABLE users ADD COLUMN created_at DATETIME DEFAULT CURRENT_TIMESTAMP;

-- Verify columns were added
DESCRIBE users;

