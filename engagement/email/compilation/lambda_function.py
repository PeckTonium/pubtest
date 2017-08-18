from __future__ import print_function
import boto3
import logging
import os
import json
import zipfile
import jinja2
from datetime import datetime

logger = logging.getLogger()
logger.setLevel(logging.INFO)
#s3_client = boto3.client('s3')


def flatten_json(y, include_dict=True, include_list=False, delimiter='__'):
    """ Flatten a JSON object. Credit: https://medium.com/@amirziai/flattening-json-objects-in-python-f5343c794b10
    :param include_dict: by default include dict
    :param include_list: by default ignore list
    :param y: the input dict object
    :param delimiter: separate keys of different levels
    :return: flattened dict object
    """
    out = {}

    def flatten(x, name=''):
        if type(x) is dict and include_dict:
            for a in x:
                flatten(x[a], name + a + delimiter)
        elif type(x) is list and include_list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + delimiter)
                i += 1
        else:
            out[name[:-len(delimiter)]] = x

    flatten(y)
    return out


def json_entry_loader(json_dict, second_level_keys=None):
    """
    Loads all top level entries from provided dictionary, and loads flattened keys from all objects specified in
    `second_level_objects_to_flatten` (if second level object contains additional dicts/lists, those are ignored). 
    :param json_dict: Input dictionary
    :param second_level_keys: List of keys to flatten and load 
    :return: single level dictionary containing non-(list/dict) entries from `json_dict` as well as non-(list/dict) 
    entries contained in nested objects specified by `second_level_keys`.
    :rtype: dict
    """
    output = dict()
    if second_level_keys is None:
        second_level_keys = list()
    for k in json_dict.iterkeys():
        if (type(json_dict[k]) is not list) and (type(json_dict[k]) is not dict):
            output[k] = json_dict[k]
    for k in second_level_keys:
        obj = json_dict.get(k)
        if not isinstance(obj, dict):
            raise NotImplementedError('json_entry_loader second level objects must be dict')
        if obj is not None:
            for k2 in obj.iterkeys():
                if (type(obj[k2]) is not list) and (type(obj[k2]) is not dict):
                    output[k + '__' + k2] = obj[k2]
    return output


def handler(event, context):
    logger.info('got event{}'.format(event))
    message = event['Records'][0]['Sns']['Message']
    if type(
            message) != dict:  # running locally this will already be dict, on AWS need to read string from SNS
        message = json.loads(message)
    json_key = message['json_key']
    bucket = message['bucket']

    # Set flag to control code execution for local vs. remote (lambda)
    if bucket == 'local':
        running_locally = True
    else:
        running_locally = False

    # Load JSON
    json_download_path = '/tmp/data.json'
    if not running_locally:
        if not os.path.isdir(os.path.dirname(json_download_path)):
            os.makedirs(os.path.dirname(json_download_path))
        logger.info('saving {} from bucket {} to {}'.format(json_key, bucket, json_download_path))
        try:
            pass #s3_client.download_file(bucket, json_key, json_download_path)
        except:
            logger.error('failed to download {}{} from s3'.format(bucket, json_key))
            raise Exception
    with open(json_download_path) as f:
        json_dict = json.load(f)
    meta_data = json_dict['metadata']

    # Load Jinja2 templates from S3
    if not running_locally:
        templates_key = 'report_cards/templates.zip'
        logger.info('saving templates from {} to {}'.format(
            bucket + '/' + templates_key, '/tmp/templates.zip'))
        try:
            pass #s3_client.download_file(bucket, templates_key, '/tmp/templates.zip')
        except:
            logger.error('failed to download templates from s3')
            raise Exception
        zip_ref = zipfile.ZipFile('/tmp/templates.zip', 'r')
        zip_ref.extractall('/tmp')
        zip_ref.close()
    logger.info('/tmp directory listing: {}'.format(os.listdir('/tmp')))

    # Render Jinja2 template specified in json
    logger.info('rendering jinja2 template')
    template_name = meta_data['template']
    template_prefix = template_name.split('_')[0]
    template_loader = jinja2.FileSystemLoader('/tmp/templates')
    template_env = jinja2.Environment(loader=template_loader)
    template = template_env.get_template(template_prefix + '/' + template_name + '.html')

    # Load view model data for jinja2
    view_model = flatten_json(json_dict['view'])
    # path to images (defaults to an empty string - i.e. charts are assumed to be in same directory as email HTML)
    view_model['S3_static_URL'] = os.getenv('S3_static_URL', '')
    if view_model['S3_static_URL'] != '':
        view_model['S3_static_URL'] += '{}/{}/'.format(
            meta_data['output_folder'], meta_data['uuid'])
    # path to static template deps
    view_model['S3_template_deps_URL'] = os.getenv('S3_template_deps_URL', '')
    logger.info('View model passed to jinja2: {}'.format(view_model))
    output = template.render(view_model)
    with open('/tmp/email.html', 'w') as f:
        f.write(output.encode("UTF-8"))

    # Upload rendered email to S3
    if running_locally:
        logger.info('DONE')
    else:
        upload_key = 'emails/{}/{}.html'.format(
            meta_data['output_folder'], meta_data['source_namespace'])
        logger.info('uploading rendered email to {}/{}'.format(bucket, upload_key))
        try:
            pass #s3_client.upload_file('/tmp/email.html', bucket, upload_key)
        except:
            logger.error('upload failed')
