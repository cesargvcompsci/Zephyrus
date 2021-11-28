# Zephyrus
The aim of this project is to create a fan that tracks groups of people in a room. With the help of computer vision, our multi-person tracking fan will be able to alternate the direction of airflow towards each group, pointing towards groups of more people for larger amounts of time. This will help combat the summer heat in a new and improved way. 

The software utilizes OpenCV to help with computer vision. The essential loop performs detection and tracking, groups people who have been detected into clusters, and updates the fan's logic to move towards groups and blow on them for a certain amount of time. The software also includes code to control GPIO from a Raspberry Pi actuate the motors of the fan.

## Usage
To run our current simulation:
```bash
python src/main.py
```