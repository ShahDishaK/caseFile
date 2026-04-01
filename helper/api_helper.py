# Importing libraries
from typing import Any, Optional
from fastapi import HTTPException, status
from dtos.base_response_model import BaseResponseModel, BaseErrorModel
import i18n


class APIHelper:
    # Send success response with custom message
    def send_error_response(errorMessageKey: Optional[str] = None, locale: Optional[str] = "en"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(BaseErrorModel(error=i18n.t(
                key=errorMessageKey or 'translations.FAILURE', locale=locale))).dict()
        )

    # Send unauthorized response with custom message
    def send_unauthorized_error(errorMessageKey: Optional[str] = None, locale: Optional[str] = "en"):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=(BaseErrorModel(error=i18n.t(
                key=errorMessageKey or 'translations.FAILURE', locale=locale))).dict()
        )

    # Send error response with custom message
    def send_success_response(data: Optional[Any] = None, successMessageKey: Optional[str] = None, locale: Optional[str] = "en"):
        return BaseResponseModel(data=data, message=i18n.t(key=successMessageKey or 'translations.SUCCESS', locale=locale)).dict()
    
    #send not found error message
    def send_not_found_error(errorMessageKey: Optional[str] = None, locale: Optional[str] = "en"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=(BaseErrorModel(error=i18n.t(
                key=errorMessageKey or 'translations.FAILURE', locale=locale))).dict()
        )
    def send_forbidden_error(errorMessageKey: Optional[str] = None, locale: Optional[str] = "en"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=(BaseErrorModel(error=i18n.t(
                key=errorMessageKey or 'translations.FAILURE', locale=locale))).dict()
        )
    def send_bad_request_error(errorMessageKey: Optional[str] = None, locale: Optional[str] = "en"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(BaseErrorModel(error=i18n.t(
                key=errorMessageKey or 'translations.FAILURE', locale=locale))).dict()
        )
