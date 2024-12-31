#!/bin/bash

# 使腳本循環執行，直到成功運行 bot.py
while true; do
  echo "Installing required Python packages..."
  pip install -r requirement.txt
  
  # 檢查 pip install 是否成功
  if [ $? -ne 0 ]; then
    echo "Failed to install dependencies. Retrying..."
    sleep 5  # 等待 5 秒鐘後重試
    continue
  fi
  
  # 執行 bot.py
  echo "Running bot.py..."
  python3 -u bot.py
  
  # 檢查 bot.py 是否成功執行
  if [ $? -ne 0 ]; then
    echo "bot.py failed to execute. Retrying..."
    sleep 5  # 等待 5 秒鐘後重試
    continue
  fi

  # 如果 bot.py 正常執行，則退出循環
  echo "Bot executed successfully!"
  break
done

