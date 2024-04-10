## Neo4j Connection Functions

This repository contains Python functions for managing a connection with Neo4j, a graph database. These functions enable you to perform various operations like creating nodes, relationships, querying data, and searching for specific entities within the database.

### Setup

To use these functions, you need to have the following setup:

1. **Neo4j Database**: Ensure you have a Neo4j database instance running.
2. **Python Environment**: Set up a Python environment with the necessary dependencies installed (`neo4j`, `dotenv`, `faker`).

### Environment Variables

Before running the code, make sure to set the required environment variables in a `.env` file:

- `NEO4J_URI`: URI for connecting to your Neo4j database.
- `NEO4J_USERNAME`: Username for authenticating the connection.
- `NEO4J_PASSWORD`: Password for authenticating the connection.

### Functions

The repository includes the following functions:

- **`createNode(labels: List[str], params=None, listOffIndexes=None, merge=False)`**: Creates a node with specified labels and properties. You can also choose to merge nodes if they already exist.
  
- **`createRelationship(node1: NodeD, node2: NodeD, type: str, properties=None, merge=True)`**: Creates a relationship between two nodes with a specified type and properties. Nodes are represented using the `NodeD` class.
  
- **`createUser(name: str, userId: str)`**, **`createMovie(title: str, movieId: str, year: int, plot: str)`**, **`createRated(userId: str, movieId: str, rating: int, timestamp: int)`**: Convenience functions for creating specific types of nodes (e.g., User, Movie) and relationships (e.g., RATED).

- **`makeQuery(query: str = 'MATCH (n) RETURN n', params=None, listOffIndexes=None)`**: Executes a Cypher query on the Neo4j database and returns the results.

- **`searchUser(userId: str = '', userName: str = '')`**, **`searchMovie(movieId: str = '', title: str = '')`**, **`searchUserWithRated(userId: str = '', userName: str = '')`**: Functions to search for specific nodes (e.g., User, Movie) or relationships (e.g., RATED) based on provided criteria.

### Usage

The main script (`__main__` block) demonstrates how to use these functions to create sample nodes and relationships, as well as how to search for and retrieve data from the Neo4j database.

### Example Scenario

In the script, we generate sample data for Users and Movies, create relationships between them (e.g., User has rated a Movie), and then perform searches based on specific criteria (e.g., search for a User with rated Movies).

### Additional Notes

- **Data Formatting**: The code includes functions for formatting properties in Cypher queries (`_format_properties`). This ensures that data types are handled correctly when constructing queries.

- **Error Handling**: Some basic error handling is included, such as validating ratings when creating rated relationships.

Feel free to explore and modify this codebase for your specific use cases involving Neo4j databases. If you have any questions or need further assistance, please let me know!
