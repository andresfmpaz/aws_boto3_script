import boto3
import json
import csv
from datetime import datetime

def extract_instance_details(price_item):
    attributes = price_item['product']['attributes']
    instance_type = attributes.get('instanceType')
    operating_system = attributes.get('operatingSystem')
    vcpu = attributes.get('vcpu')
    memory = attributes.get('memory')
    instance_family = attributes.get('instanceFamily')
    return instance_type, operating_system, vcpu, memory, instance_family

def extract_price(price_item):
    on_demand = price_item['terms'].get('OnDemand', {})
    for offer in on_demand.values():
        price_dimensions = next(iter(offer['priceDimensions'].values()))
        if 'USD' in price_dimensions['pricePerUnit']:
            price_per_unit = price_dimensions['pricePerUnit']['USD']
            return float(price_per_unit)
    return 0.0

def get_instance_info(region_name):
    client = boto3.client('pricing', region_name='us-east-1')
    timestamp_actual = datetime.now()

    timestamp_formateado = timestamp_actual.strftime('%Y_%m_%d_%H_%M_%S')
    with open('/path/instance_details1'+timestamp_formateado+'.csv', 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(['Family', 'Instance Type', 'vCPU', 'Memory', 'Operating System', 'Price'])

        next_token = None
        while True:
            params = {
                'ServiceCode': 'AmazonEC2',
                'Filters': [
                    {'Type': 'TERM_MATCH', 'Field': 'location', 'Value': 'US East (N. Virginia)'}
                ],
                'MaxResults': 100
            }
            if next_token:
                params['NextToken'] = next_token

            response = client.get_products(**params)

            for price_item_str in response['PriceList']:
                price_item = json.loads(price_item_str)
                instance_type, operating_system, vcpu, memory, instance_family = extract_instance_details(price_item)
                price = extract_price(price_item)
                writer.writerow([instance_family, instance_type, vcpu, memory, operating_system, price])

            next_token = response.get('NextToken')
            if not next_token:
                break

if __name__ == "__main__":
    get_instance_info("us-east-1")    
