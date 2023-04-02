#
from qencode.const import *
from botocore.exceptions import ClientError
import boto3
import requests
from requests.utils import quote
import xml.etree.cElementTree as et
import uuid


def generate_aws_signed_url(region, bucket, object_key, access_key, secret_key, expiration, endpoint=None):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """
    session = boto3.Session(aws_access_key_id= access_key, 
                            aws_secret_access_key=secret_key,
                            region_name=region)
    # Generate a presigned URL for the S3 object
    s3_client = session.client('s3')
    endpointUrl = s3_client.meta.endpoint_url
    s3_client = session.client('s3', endpoint_url=endpointUrl)
    try:
        response = s3_client.generate_presigned_url('get_object',
                                                    Params={'Bucket': bucket,
                                                            'Key': object_key},
                                                    ExpiresIn=expiration)
    except ClientError as e:
        return None

    # The response contains the presigned URL
    return response


def fps_drm(username, password, uid=None):
    asset_id = uid if uid else uuid.uuid4()
    url = FPS_DRM_KEYGENERATOR_URI_TEMPLATE % (asset_id, username, password)
    response = requests.post(url, {})
    tree = et.ElementTree(et.fromstring(response.content))
    root = tree.getroot()
    kid = root[0][0].get('kid')
    iv = root[0][0].get('explicitIV')
    key = root[0][0][0][0][0].text
    key_hex = key.decode('base64').encode('hex')
    iv_hex = iv.decode('base64').encode('hex')
    key_url = DRM_KEY_URL_TEMPLATE % kid
    payload = dict(AssetID=asset_id)
    data = dict(key=key_hex, iv=iv_hex, key_url=key_url)
    return data, payload


def cenc_drm(username, password, uid=None):
    asset_id = uid if uid else uuid.uuid4()
    url = CENC_DRM_KEYGENERATOR_URI_TEMPLATE % (asset_id, username, password)
    response = requests.post(url, {})
    tree = et.ElementTree(et.fromstring(response.content))
    root = tree.getroot()
    key_id = root[0][0].get('kid')
    key = root[0][0][0][0][0].text
    pssh = root[1][0][0].text
    key_id_hex = key_id.replace('-', '')
    key_hex = key.decode('base64').encode('hex')
    key_url = DRM_KEY_URL_TEMPLATE % key_id
    payload = dict(AssetID=asset_id)
    data = dict(key=key_hex, key_id=key_id_hex, pssh=pssh, key_url=key_url)
    return data, payload
