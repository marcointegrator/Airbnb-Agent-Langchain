from tools.rag_memory_tool import clear_chroma_database


def main():
    message = clear_chroma_database()
    print(message)


if __name__ == "__main__":
    main()
