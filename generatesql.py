from  flask import flash
import openai
import sqlparse

openai.api_key = "Your_Openai_key_here"

class GenerateSQL:
    def generate_sql(self, question, structure):
        # Check if question and structure are not null
        if not question or not structure:
            flash('Question or structure cannot be null.')
            return None

        try:
            response = openai.Completion.create(
                engine="text-davinci-003",
                prompt=f"The database structure is: '{structure}'. Generate and give me the SQL query only for this question: '{question}'",
                max_tokens=200,
                n=1,
                stop=None,
                temperature=0.2,
            )
            answer = response.choices[0].text.strip()

            # Check if the SQL query is valid
            try:
                sqlparse.parse(answer)
                return answer
            except sqlparse.exceptions.SQLParseError:
                flash('Generated SQL query is not valid.')
                return None

        except Exception as e:
            flash('Failed to generate Sql Query please ask your question again on different way')
            return None
