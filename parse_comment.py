import sys
import yaml

def main():
    comment_body = sys.argv[1]

    # Split comment_body into front matter and YAML content
    front_matter, yaml_content = comment_body.split('---', 2)[1:]

    # Parse YAML content
    parsed_data = yaml.safe_load(yaml_content.strip())

    # Print parsed data
    print("Front Matter:")
    print(front_matter.strip())
    print("\nParsed YAML Data:")
    print(parsed_data)

if __name__ == "__main__":
    main()
