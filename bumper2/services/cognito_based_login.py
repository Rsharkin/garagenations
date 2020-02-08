import logging
import boto3
from botocore.exceptions import ClientError
from . import settings
logger = logging.getLogger(__name__)


def get_aws_open_id_token(username):
    client = boto3.client('cognito-identity', settings.COGNITO_AWS_REGION,
                          aws_access_key_id=settings.COGNITO_ACCESS_KEY_ID,
                          aws_secret_access_key=settings.COGNITO_SECRET_ACCESS_KEY)

    # It requires the Role to have access to cognito
    # Given a valid user , the API should return the Cognito Resp
    # return directly to the client
    # See http://docs.aws.amazon.com/cognito/devguide/identity/concepts/authentication-flow/
    logger.info('Requesting open_id from Cognito for: {0}'.format(username))
    resp = None
    try:
        resp = client.get_open_id_token_for_developer_identity(
            IdentityPoolId=settings.IDENTITY_POOL_ID,
            Logins={settings.DEVELOPER_PROVIDED_NAME: str(username)}
        )
        logger.info("Identity ID: {0}".format(resp['IdentityId']))
        logger.info("Request ID : {0}".format((resp['ResponseMetadata']['RequestId'])))
    except ClientError as e:
        logger.exception(str(e))

    return resp
