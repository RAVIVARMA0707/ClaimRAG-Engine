class QueryServices:

    @staticmethod
    def format_results(query: str, context: str) -> dict:
        """
        Formats agent-retrieved context into a standard response.
        """
        return {
            "query": query,
            "results": context,
        }
