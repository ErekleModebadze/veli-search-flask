import os


class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')

    BM25_FILE_ID = os.getenv('BM25_FILE_ID', 'aXh0jvOpIzkoKIxjX7bIh06K4fDgER9i')

    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = os.getenv('SQLALCHEMY_TRACK_MODIFICATIONS', False)

    PINECONE_HOST = os.getenv('PINECONE_HOST')
    PINECONE_API_KEY = os.getenv('PINECONE_API_KEY')

    DEEPINFRA_HOST = os.getenv('DEEPINFRA_HOST', 'https://api.deepinfra.com/v1/openai')
    DEEPINFRA_API_KEY = os.getenv('DEEPINFRA_API_KEY')
