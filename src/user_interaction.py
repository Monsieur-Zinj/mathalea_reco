def get_optional_tags():
    tags = {}
    while True:
        tag = input("Enter a tag (or press Enter to finish): ").strip()
        if not tag:
            break
        value = input(f"Enter value for {tag}: ").strip()
        tags[tag] = value
    return tags
