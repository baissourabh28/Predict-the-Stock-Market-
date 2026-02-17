"""
Input validation utilities
"""
import re
from typing import Optional
from fastapi import HTTPException, status


class InputValidator:
    """Validators for user input"""
    
    # Allowed symbol pattern: alphanumeric, dash, underscore, max 20 chars
    SYMBOL_PATTERN = re.compile(r'^[A-Z0-9_-]{1,20}$')
    
    @staticmethod
    def validate_symbol(symbol: str) -> str:
        """
        Validate trading symbol to prevent injection attacks
        
        Args:
            symbol: Trading symbol to validate
            
        Returns:
            Validated symbol in uppercase
            
        Raises:
            HTTPException: If symbol is invalid
        """
        if not symbol:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Symbol cannot be empty"
            )
        
        # Convert to uppercase
        symbol = symbol.upper().strip()
        
        # Check pattern
        if not InputValidator.SYMBOL_PATTERN.match(symbol):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid symbol format. Use only letters, numbers, dash, and underscore (max 20 chars)"
            )
        
        return symbol
    
    @staticmethod
    def validate_timeframe(timeframe: str) -> str:
        """
        Validate timeframe parameter
        
        Args:
            timeframe: Timeframe string
            
        Returns:
            Validated timeframe
            
        Raises:
            HTTPException: If timeframe is invalid
        """
        valid_timeframes = ['1m', '5m', '15m', '1H', '1D', '1W']
        
        if timeframe not in valid_timeframes:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid timeframe. Must be one of: {', '.join(valid_timeframes)}"
            )
        
        return timeframe
    
    @staticmethod
    def sanitize_string(value: str, max_length: int = 500) -> str:
        """
        Sanitize string input
        
        Args:
            value: String to sanitize
            max_length: Maximum allowed length
            
        Returns:
            Sanitized string
        """
        if not value:
            return ""
        
        # Remove null bytes and control characters
        sanitized = ''.join(char for char in value if ord(char) >= 32 or char in '\n\r\t')
        
        # Truncate to max length
        return sanitized[:max_length]
