import sys
import yaml

def main():
    comment_body = sys.argv[1]

    # Check if there is a front matter section
    if '---' in comment_body:
        # Split comment_body into front matter and YAML content
        front_matter, yaml_content = comment_body.split('---', 2)[1:]
        parsed_data = yaml.safe_load(yaml_content.strip())
    else:
        # If no front matter, assume the entire comment body is YAML content
        parsed_data = yaml.safe_load(comment_body.strip())

    # Print parsed data
    print(parsed_data)

if __name__ == "__main__":
    main()
