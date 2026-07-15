from rag.document_builder import DocumentBuilder


class ProviderLookup:
    """
    Builds a fast lookup dictionary for Provider IDs.
    """

    def __init__(self):

        builder = DocumentBuilder()

        builder.load_data()
        builder.prepare_claims()
        builder.merge_provider_labels()
        builder.calculate_provider_statistics()
        builder.build_provider_documents()

        self.lookup = {}

        for document in builder.get_documents():

            provider_id = document.metadata.get("provider_id")

            if provider_id:
                self.lookup[provider_id.upper()] = document

    def get_provider(self, provider_id: str):

        return self.lookup.get(provider_id.upper())