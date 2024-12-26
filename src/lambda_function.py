import json
import boto3

region = 'us-east-1'
dynamodb = boto3.resource('dynamodb', region_name=region)
dynamodb_table_name = 'JayB-Test-DynamoDB-List'

ENDPOINTS = {
    ('GET', '/item'): lambda event: get_item(event['queryStringParameters']['itemId']),
    ('GET', '/items'): lambda _: get_items(),
    ('POST', '/item'): lambda event: save_item(json.loads(event['body'])),
    ('PATCH', '/item'): lambda event: modify_item(json.loads(event['body'])),
    ('DELETE', '/item'): lambda event: delete_item(json.loads(event['body'])['itemId']),
}

def lambda_handler(event, context):
    print('Request event: ', event)
    action = ENDPOINTS.get((event['httpMethod'], event['path']))
    response = action(event) if action else build_response(404, '404 Not Found')
    return response

def get_item(item_id):
    table = dynamodb.Table(dynamodb_table_name)
    response = table.get_item(Key={'itemId': item_id})
    return build_response(200, response['Item']) if 'Item' in response else build_response(404, 'Item not found')

def get_items():
    table = dynamodb.Table(dynamodb_table_name)
    items = table.scan().get('Items', [])
    return build_response(200, {'items': items})

def save_item(item):
    dynamodb.Table(dynamodb_table_name).put_item(Item=item)
    return build_response(200, {'Operation': 'SAVE', 'Message': 'SUCCESS', 'Item': item})

def modify_item(request_body):
    table = dynamodb.Table(dynamodb_table_name)
    response = table.update_item(
        Key={'itemId': request_body['itemId']},
        UpdateExpression=f'set {request_body["updateKey"]} = :value',
        ExpressionAttributeValues={':value': request_body['updateValue']},
        ReturnValues='UPDATED_NEW'
    )
    return build_response(200, {'Operation': 'UPDATE', 'Message': 'SUCCESS', 'UpdatedAttributes': response})

def delete_item(item_id):
    response = dynamodb.Table(dynamodb_table_name).delete_item(
        Key={'itemId': item_id},
        ReturnValues='ALL_OLD'
    )
    return build_response(200, {'Operation': 'DELETE', 'Message': 'SUCCESS', 'Item': response})

def build_response(status_code, body=None):
    return {
        'statusCode': status_code,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps(body or {})
    }
