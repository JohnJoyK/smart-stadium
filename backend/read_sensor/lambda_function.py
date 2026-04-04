import json
import boto3
from boto3.dynamodb.conditions import Key
from datetime import datetime, timedelta

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('StadiumSensorData')

HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type',
    'Access-Control-Allow-Methods': 'GET,OPTIONS'
}

def lambda_handler(event, context):
    try:
        path = event.get('path', '/')
        http_method = event.get('httpMethod', 'GET')

        if http_method == 'OPTIONS':
            return {'statusCode': 200, 'headers': HEADERS, 'body': ''}

        if path == '/sensors/latest':
            return get_latest_all()

        elif path.startswith('/sensors/'):
            sensor_type = path.split('/')[-1]
            return get_sensor_history(sensor_type)

        elif path == '/alerts':
            return get_alerts()

        else:
            return {
                'statusCode': 404,
                'headers': HEADERS,
                'body': json.dumps({'error': 'Route not found'})
            }

    except Exception as e:
        print(f"Error: {e}")
        return {
            'statusCode': 500,
            'headers': HEADERS,
            'body': json.dumps({'error': str(e)})
        }

def get_latest_all():
    sensor_types = ['air_quality', 'noise_level', 'queue_wait']
    result = {}

    for sensor_type in sensor_types:
        response = table.query(
            KeyConditionExpression=Key('sensor_type').eq(sensor_type),
            ScanIndexForward=False,
            Limit=1
        )
        if response['Items']:
            result[sensor_type] = response['Items'][0]

    return {
        'statusCode': 200,
        'headers': HEADERS,
        'body': json.dumps(result, default=str)
    }

def get_sensor_history(sensor_type):
    since = (datetime.utcnow() - timedelta(minutes=30)).isoformat()

    response = table.query(
        KeyConditionExpression=Key('sensor_type').eq(sensor_type) & Key('timestamp').gte(since),
        ScanIndexForward=True,
        Limit=50
    )

    return {
        'statusCode': 200,
        'headers': HEADERS,
        'body': json.dumps(response['Items'], default=str)
    }

def get_alerts():
    sensor_types = ['air_quality', 'noise_level', 'queue_wait']
    alerts = []

    for sensor_type in sensor_types:
        response = table.query(
            KeyConditionExpression=Key('sensor_type').eq(sensor_type),
            ScanIndexForward=False,
            Limit=1
        )
        if response['Items']:
            item = response['Items'][0]
            data = item.get('data', {})

            if sensor_type == 'air_quality' and data.get('alert'):
                alerts.append({
                    'type': 'air_quality',
                    'severity': 'warning',
                    'message': f"Poor air quality detected — AQI: {data.get('latest_aqi', 'unknown')}"
                })

            if sensor_type == 'noise_level' and data.get('avg_decibels', 0) > 100:
                alerts.append({
                    'type': 'noise_level',
                    'severity': 'info',
                    'message': f"High noise level: {data.get('avg_decibels')} dB"
                })

            if sensor_type == 'queue_wait':
                best = data.get('best_stand')
                wait = data.get('best_wait_minutes')
                if wait and wait < 5:
                    alerts.append({
                        'type': 'queue_wait',
                        'severity': 'success',
                        'message': f"Best time to buy snacks — {best} has only {wait} min wait!"
                    })

    return {
        'statusCode': 200,
        'headers': HEADERS,
        'body': json.dumps({'alerts': alerts}, default=str)
    }