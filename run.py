import argparse
import sys
import os

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', type=str, choices=['dev', 'pro'])
    args = parser.parse_args()
    # 分析参数，然后运行
    import src.db.orm

