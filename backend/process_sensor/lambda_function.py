import json
import boto3
from datetime import datetime
from decimal import Decimal

dynamodb = boto3.resource('dynamodb', region_name='us-east-1')
table = dynamodb.Table('StadiumSensorData')

def convert_floats(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, int):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: convert_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_floats(i) for i in obj]
    elif isinstance(obj, bool):
        return obj
    else:
        return obj

def lambda_handler(event, context):
    processed = 0

    for record in event['Records']:
        try:
            body = json.loads(record['body'])
            body = convert_floats(body)

            sensors = body.get('sensors', {})
            timestamp = body.get('timestamp', datetime.utcnow().isoformat())
            fog_node_id = body.get('fog_node_id', 'unknown')

            for sensor_type, sensor_data in sensors.items():
                item = {
                    'sensor_type': str(sensor_type),
                    'timestamp': str(timestamp),
                    'fog_node_id': str(fog_node_id),
                    'data': sensor_data,
                    'reading_count': body.get('reading_count', 0)
                }
                table.put_item(Item=item)
                print(f"Stored {sensor_type} reading at {timestamp}")
                processed += 1

        except Exception as e:
            print(f"Error processing record: {e}")
            raise e

    return {
        'statusCode': 200,
        'body': json.dumps(f'Processed {processed} sensor readings')
    }