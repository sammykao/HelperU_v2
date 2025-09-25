def main():
    with open("./PushTokenSecret.p8", "r") as file:
        key = file.read()
        encoded_key = key.replace("\n", "\\n")
        print(encoded_key)

        print()


if __name__ == "__main__":
    main()
