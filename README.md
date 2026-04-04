## SMART STADIUM EXPERIENCE ENHANCEMENT SYSTEM
# A Fog Computing Project for Large Venues

OVERVIEW
--------
This system is implemented to understand the concepts of Fog and
edge computing fundamentals. It simulates a Smart Stadium IoT 
solution that mocks sensors, a virtual fog node and a backend on 
AWS. Its collects the mock sensor data from 3 sensors, namely 
Air quality, Noise level and Queue sensors, process them on the 
Fog layer, dispatches to AWS IoT core, stores the processed
data in DynamoDB and visualise them as graphs in the React Frontend.

Data flow:
  Sensors → MQTT → Fog Node → AWS IoT Core → SQS → Lambda
  → DynamoDB → API Gateway → React Frontend


PREREQUISITES

SOFTWARE REQUIREMENTS
---------------------
- Python 3.8 or higher       https://www.python.org/downloads/
- Node.js 18 or higher       https://nodejs.org/
- Mosquitto MQTT broker      https://mosquitto.org/download/
- AWS CLI v2                 https://aws.amazon.com/cli/
- Git                        https://git-scm.com/

AWS REQUIREMENTS
----------------
- An active AWS account
- AWS CLI configured with your credentials (run: aws configure)
- The following AWS services provisioned:
    - AWS IoT Core (Thing + certificates)
    - SQS Queue:     StadiumSensorQueue
    - DynamoDB Table: StadiumSensorData
    - Lambda Functions:
        - stadium-process-sensor
        - stadium-read-sensor
    - API Gateway (deployed via AWS SAM)



## INSTALLATION

STEP 1 — CLONE THE REPOSITORY
------------------------------
  git clone https://github.com/JohnJoyK/smart-stadium.git
  cd smart-stadium


STEP 2 — SET UP PYTHON ENVIRONMENT
------------------------------------
  python3 -m venv venv

  # Mac / Linux
  source venv/bin/activate

  # Windows
  venv\Scripts\activate

  pip install paho-mqtt boto3 awsiotsdk


STEP 3 — ADD IOT CERTIFICATES
------------------------------
Place the public, private key files in the fog_node/certs/ directory.
These are to be downloaded from AWS IoT Core when creating your Thing


STEP 4 — CONFIGURE THE FOG NODE
---------------------------------
Open fog_node/fog_node.py and update the following values:

  AWS_ENDPOINT = "IOT Endpoint"


STEP 5 — SET UP AWS IOT CORE RULE
-----------------------------------
Create an IoT rule to route messages from the fog node to SQS:

  Rule name:    StadiumSensorRule
  SQL:          SELECT * FROM 'stadium/fog/processed'
  Action:       Send to SQS queue -> StadiumSensorQueue


STEP 6 — DEPLOY LAMBDA FUNCTIONS
----------------------------------
Copy the code from the following files into the AWS Lambda console:

  backend/process_sensor/lambda_function.py
    Lambda function: stadium-process-sensor
    Trigger: SQS (StadiumSensorQueue)

  backend/read_sensor/lambda_function.py
    Lambda function: stadium-read-sensor
    Trigger: API Gateway


STEP 7 — SET UP THE REACT DASHBOARD
-------------------------------------
  cd dashboard
  npm install

Create a .env file in the dashboard/ folder:
  VITE_API_URL=https://YOUR_API_GATEWAY_URL/Prod


## RUNNING THE SYSTEM

Open 5 terminals with the python environment

TERMINAL 1 — Start MQTT Broker
--------------------------------
  mosquitto

TERMINAL 2 — Start Fog Node
-----------------------------
  cd smart-stadium
  python fog_node/fog_node.py

TERMINAL 3 — Start Air Quality Sensor
---------------------------------------
  cd smart-stadium
  python sensors/sensor_airquality.py

TERMINAL 4 — Start Noise Sensor
---------------------------------
  cd smart-stadium
  python sensors/sensor_noise.py

TERMINAL 5 — Start Queue Sensor
---------------------------------
  cd smart-stadium
  python sensors/sensor_queue.py

TERMINAL 6 — Start React Dashboard
------------------------------------
  cd smart-stadium/dashboard
  npm run dev

Open http://localhost:5173 in your browser.
The dashboard updates automatically every 5 seconds.

