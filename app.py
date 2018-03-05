from chalice import Chalice, Response
import boto3
#import urllib
#import requests
from urllib.parse import urlparse, parse_qs

app = Chalice(app_name='chalice-ec2-slack-bot')

# S3 = boto3.client('s3', region_name='us-west-2')
# session = boto3.Session(profile_name='PROFILE')
# session = boto3.Session()
# ec2client = session.client('ec2') #, region_name='us-east-1')
ec2client = boto3.client('ec2', region_name='us-east-1')


# ec2client = boto3.client('ec2', region_name='us-east-1')

SLACK_TOKEN = 'YOUR_SLACK_TOKEN'


def get_tag_value(tags, tag_key):
    tag_pair = [tag for tag in tags if 'Key' in tag and tag['Key'] == tag_key]
    print(tag_pair)
    if len(tag_pair) > 0:
        return tag_pair[0].get('Value', 'unknown')
    else:
        return 'unknown'


@app.route('/')
def index():
    return {'status': 'ok'}


@app.route('/servers', methods=['POST'],
           content_types=['application/x-www-form-urlencoded'])
def servers():
    try:
        instances = []
        response = ec2client.describe_instances()
        for reservation in response["Reservations"]:
            for instance in reservation["Instances"]:
                print("Ok")
                tags = instance.get('Tags', [])
                print(tags)

                print("Ok1")
                instances.append({
                    'Name': get_tag_value(tags, 'Name'),
                    'InstanceType': instance.get('InstanceType', 'unknown'),
                    'State': instance.get('State', {}).get('Name', 'unknown')
                })

                print("Ok2")

                # instance["Reservations"][0]["Instances"][0]

                instance['LaunchTime'] = None
                instance['BlockDeviceMappings'] = None
                instance['NetworkInterfaces'] = None
                 #instanceA = response["Reservations"][0]["Instances"][0]

        # instanceA['LaunchTime'] = None
        # instanceA['BlockDeviceMappings'] = None
        # instanceA['NetworkInterfaces'] = None

        # return {'hello': 'world'}
        # return Response(body=str(instanceA.keys()),
        # return Response(body=str(response["Reservations"][0]["Instances"][0].keys()),
        # return Response(body=str(response["Reservations"][0]["Instances"][0]['InstanceId']),

        json = parse_qs(app.current_request.raw_body.decode())
        #print(json)

        #json = app.current_request.query_params
        # retrieve card information from slack query
        # card_name = urllib.quote_plus(json['text'])
        # try to derive the card name from a fragment
        # cards_json = requests.get(GATHERER_TYPEAHEAD_URI % card_name).json()
        # remember that slack token?, let's safeguard here
        if json['token'] == [SLACK_TOKEN]:
            # card_name = cards_json['Results'][0]['Name']
            # Get card image uri - important to urlescape the card name
            # response = GATHERER_URI % urllib.quote_plus(card_name)

            attachments = [{
                "text": i['Name'] + " | " + i['State'],
                "actions": [
                    {
                        "name": "action",
                        "text": "Stop",
                        "type": "button",
                        "value": "stop"
                    },
                    {
                        "name": "action",
                        "text": "Start",
                        "type": "button",
                        "value": "start"
                    }
                ]
            } for i in instances]
            out_json = {
              "response_type": "in_channel",
              "attachments": attachments
              #"attachments": [
              #  {
              #    "text": str(instances)
              #      #,
              #    #"text": json['text'],
              #    #"image_url": response,
              #  }
              #]
            }
            return out_json
        else:
            return {"text": "Card not found"}

        # return Response(body=str(response),
        #                status_code=200,
        #                headers={'Content-Type': 'text/plain'})

    except Exception as e:
        return e

    # return {'hello': 'world'}


# The view function above will return {"hello": "world"}
# whenever you make an HTTP GET request to '/'.
#
# Here are a few more examples:
#
# @app.route('/hello/{name}')
# def hello_name(name):
#    # '/hello/james' -> {"hello": "james"}
#    return {'hello': name}
#
# @app.route('/users', methods=['POST'])
# def create_user():
#     # This is the JSON body the user sent in their POST request.
#     user_as_json = app.current_request.json_body
#     # We'll echo the json body back to the user in a 'user' key.
#     return {'user': user_as_json}
#
# See the README documentation for more examples.
#
