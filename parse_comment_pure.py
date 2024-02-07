import sys
import yaml

def main():
    comment_body = sys.argv[1]

    # Remove the '---' delimiter if it exists
    comment_body = comment_body.replace('---', '')

    # Parse the entire comment body as YAML content
    parsed_data = yaml.safe_load(comment_body.strip())

    # Print parsed data
    print(parsed_data)

if __name__ == "__main__":
    main()
