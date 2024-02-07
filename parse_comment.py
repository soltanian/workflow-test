import sys
import yaml

def main():
    comment_body = sys.argv[1]
    parsed_data = yaml.safe_load(comment_body)
    print(parsed_data)

if __name__ == "__main__":
    main()
