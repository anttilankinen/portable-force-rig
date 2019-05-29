#!/usr/bin/env bash

echo "Starting portable force rig application.."
docker-compose up -d &
cd ./service.calibration && python3 main.py &
cd ./service.video-stream && python3 main.py &
