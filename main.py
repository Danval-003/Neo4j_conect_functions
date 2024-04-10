# This is a sample Python script.
import os
from typing import LiteralString
from neo4j import GraphDatabase, Result, graph
from typing import *
import datetime
import faker as faker
import random

# Press Mayús+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()
uri = os.getenv('NEO4J_URI')
username = os.getenv('NEO4J_USERNAME')
password = os.getenv('NEO4J_PASSWORD')

neo4j_driver = GraphDatabase.driver(uri,
                                    auth=(username, password))


def _format_properties(properties):
    # Formatear las propiedades para la consulta Cypher
    if not properties:
        return ""

    def typed(val):
        if isinstance(val, str):
            return f"'{val.replace('\'', '\\\'')}'"
        if isinstance(val, bool):
            return str(val).lower()
        if isinstance(val, dict):
            return "{" + ", ".join(f"{key}: {typed(value)}" for key, value in val.items()) + "}"
        if isinstance(val, list):
            return "[" + ", ".join(typed(value) for value in val) + "]"
        if isinstance(val, int):
            return str(val)
        if isinstance(val, float):
            return str(val)
        if isinstance(val, datetime.date):
            return f"date('{val}')"
        return str(val)

    formatted_props = "{" + ", ".join(f"{key}: {typed(value)}" for key, value in properties.items()) + "}"
    return formatted_props


class NodeD:
    def __init__(self, labels, properties):
        self.labels = labels
        self.properties = properties

    def to_json(self):
        return self.__dict__

    def __str__(self):
        return str(self.to_json())


class RelationshipD:
    def __init__(self, type, properties, node1: 'NodeD', node2: 'NodeD'):
        self.type = type
        self.properties = properties
        self.node1 = node1.to_json()
        self.node2 = node2.to_json()

    def to_json(self):
        return self.__dict__

    def __str__(self):
        return f'{self.node1} - {self.type} - {self.node2} ' + str(self.properties)


def transFormObject(obj):
    if isinstance(obj, graph.Node):
        labels = list(obj.labels)
        properties = dict(obj)
        return NodeD(labels, properties)
    elif obj is not None:
        nodesR = [transFormObject(ls) for ls in obj.nodes]
        typeR = obj.type
        properties = dict(obj)
        return RelationshipD(typeR, properties, nodesR[0], nodesR[1])

    return obj


def createNode(labels: List[str], params=None, listOffIndexes=None, merge=False):
    if listOffIndexes is None:
        listOffIndexes = ['n']
    if params is None:
        params = {}

    with neo4j_driver.session() as session:
        cypher_query: LiteralString = f"CREATE (node:`{':'.join(labels)}` {_format_properties(params)})"
        if merge:
            cypher_query = f"MERGE (node:{':'.join(labels)} {_format_properties(params)})"
        session.run(cypher_query)


def createRelationship(node1: NodeD, node2: NodeD, type: str, properties=None, merge=True):
    if properties is None:
        properties = {}

    with neo4j_driver.session() as session:
        cypher_query: LiteralString = f"MATCH (a:{':'.join(node1.labels)} {_format_properties(node1.properties)}) " \
                                      f"MATCH (b:{':'.join(node2.labels)} {_format_properties(node2.properties)}) " \
                                      f"CREATE (a)-[r:{type} {_format_properties(properties)}]->(b)"
        if merge:
            cypher_query = f"MATCH (a:{':'.join(node1.labels)} {_format_properties(node1.properties)}) " \
                            f"MATCH (b: {':'.join(node2.labels)} {_format_properties(node2.properties)}) " \
                            f"MERGE (a)-[r:{type} {_format_properties(properties)}]->(b)"
        session.run(cypher_query)


def createUser(name: str, userId: str):
    createNode(['User'], {'name': name, 'userId': userId}, merge=True)


def createMovie(title: str, movieId: str, year: int, plot: str):
    createNode(['Movie'], {'title': title, 'movieId': movieId, 'year': year, 'plot': plot}, merge=True)


def createRated(userId: str, movieId: str, rating: int, timestamp: int):
    if rating not in range(1, 6):
        raise ValueError("Rating must be between 1 and 5.")
    createNode(['User'], {'userId': userId}, merge=True)
    createNode(['Movie'], {'movieId': movieId}, merge=True)
    createRelationship(NodeD(['User'], {'userId': userId}), NodeD(['Movie'], {'movieId': movieId}), 'RATED',
                       {'rating': rating, 'timestamp': timestamp})


def makeQuery(query: LiteralString = 'MATCH (n) RETURN n', params=None, listOffIndexes=None):
    if listOffIndexes is None:
        listOffIndexes = ['n']
    if params is None:
        params = {}

    with neo4j_driver.session() as session:
        print("Session started successfully.")
        nodes: Result = session.run(query, params)
        records = []
        for n in nodes:
            records.append(tuple([transFormObject(n[index]) for index in listOffIndexes]))
        return records


def searchUser(userId: str = '', userName: str = ''):
    properties = {}
    if userName != '':
        properties['name'] = userName
    if userId != '':
        properties['userId'] = userId

    records = makeQuery(f"MATCH (u:User {_format_properties(properties)}) RETURN u", listOffIndexes=['u'])
    if len(records) == 0:
        return None
    userNode = records[0][0]

    return userNode.to_json()


def searchMovie(movieId: str = '', title: str = ''):
    properties = {}
    if title != '':
        properties['title'] = title
    if movieId != '':
        properties['movieId'] = movieId

    records = makeQuery(f"MATCH (m:Movie {_format_properties(properties)}) RETURN m", listOffIndexes=['m'])
    if len(records) == 0:
        return None
    movieNode = records[0][0]

    return movieNode.to_json()


def searchUserWithRated(userId: str = '', userName: str = ''):
    properties = {}
    if userName != '':
        properties['name'] = userName
    if userId != '':
        properties['userId'] = userId

    records = makeQuery(f"MATCH (u:User {_format_properties(properties)})-[r:RATED]->(m:Movie) RETURN u, r, m",
                        listOffIndexes=['u', 'r', 'm'])
    if len(records) == 0:
        return None

    toret = []

    for record in records:
        userNode = record[0]
        ratedNode = record[1]
        movieNode = record[2]
        toret.append((userNode.to_json(), ratedNode.to_json(), movieNode.to_json()))

    return toret


# Press the green button in the gutter to run the script.
if __name__ == '__main__':


    # Crear usuarios y películas de prueba
    movies = []
    movieNames = []
    for _ in range(5):
        movieId = faker.Faker().uuid4()
        movieName = faker.Faker().sentence()
        createMovie(movieName, movieId, faker.Faker().year(), faker.Faker().sentence())
        movies.append(movieId)
        movieNames.append(movieName)


    otherMovies = movies.copy()
    usernames = []
    for _ in range(5):
        random.shuffle(otherMovies)
        movieId = otherMovies.pop()
        if len(otherMovies) == 0:
            otherMovies = movies.copy()
        movieId2 = movieId

        while movieId2 == movieId:
            movieId2 = otherMovies.pop()
            if len(otherMovies) == 0:
                otherMovies = movies.copy()

        userId = faker.Faker().uuid4()
        usernameS = faker.Faker().name()
        createUser(usernameS, userId)
        createRated(userId, movieId, random.randint(1, 5), faker.Faker().unix_time())
        createRated(userId, movieId2, random.randint(1, 5), faker.Faker().unix_time())
        usernames.append(usernameS)

    random.shuffle(usernames)
    usN = usernames[0]
    print(f"User to search: {usN}")
    random.shuffle(movieNames)
    mN = movieNames[0]
    print(f"Movie to search: {mN}")
    # Buscar usuarios y películas de prueba
    uR = searchUserWithRated(userName=usN)
    u = searchUser(userName=usN)
    m = searchMovie(title=mN)

    if u is not None:
        print("User found.")
        print(u)
        print()
    else:
        print("User not found.")

    if m is not None:
        print("Movie found.")
        print(m)
        print()
    else:
        print("Movie not found.")

    if uR is not None:
        print("User with relations Rated found.")
        for record in uR:
            print('User:', record[0])
            print('Rated Relation:', record[1])
            print('Movie:', record[2])
            print()
    else:
        print("User with relations Rated not found.")

    # Buscar usuarios y películas de prueba

    personActorDirectorProperties = {
        'name': 'Tom Hanks',
        'tmdbld': 31,
        'imdbld': 31,
        'born': datetime.date(1956, 7, 9),
        'bio': 'Thomas Jeffrey Hanks is an American actor and filmmaker. Known for both his comedic and dramatic roles, Hanks is one of the most popular and recognizable film stars worldwide, and is widely regarded as an American cultural icon.',
        'died': datetime.date(2021, 7, 9),
        'bornIn': 'Concord, California, USA',
        'url': 'https://en.wikipedia.org/wiki/Tom_Hanks',
        'poster': 'https://en.wikipedia.org/wiki/Tom_Hanks#/media/File:Tom_Hanks_2019_by_Glenn_Francis.jpg'
    }

    personActor = {
        'name': 'Keanu Reeves',
        'tmdbld': 6384,
        'imdbld': 6384,
        'born': datetime.date(1964, 9, 2),
        'bio': 'Keanu Charles Reeves is a Canadian actor. Born in Beirut and raised in Toronto, Reeves began acting '
               'in theatre productions and in television films before making his feature film debut in Youngblood ('
               '1986). He had his breakthrough role in the science fiction comedy Bill & Ted\'s Excellent Adventure ('
               '1989), and he later reprised his role in its sequels.',
        'bornIn': 'Beirut, Lebanon',
        'url': 'https://en.wikipedia.org/wiki/Keanu_Reeves',
        'poster': 'https://en.wikipedia.org/wiki/Keanu_Reeves#/media/File:Keanu_Reeves_(crop_and_levels)_(cropped).jpg',
        'died': datetime.date(2021, 7, 9)
    }

    personDirector = {
        'name': 'Steven Spielberg',
        'tmdbld': 488,
        'imdbld': 488,
        'born': datetime.date(1946, 12, 18),
        'bio': 'Steven Allan Spielberg is an American film director, producer, and screenwriter. He began his career '
               'in the New Hollywood era and is currently the most commercially successful director. Spielberg is the '
               'recipient of various accolades, including three Academy Awards, a Kennedy Center honor, and a Cecil B. '
               'DeMille Award.',
        'bornIn': 'Cincinnati, Ohio, USA',
        'url': 'https://en.wikipedia.org/wiki/Steven_Spielberg',
        'poster': 'https://en.wikipedia.org/wiki/Steven_Spielberg#/media/File:Steven_Spielberg_by_Gage_Skidmore.jpg',
        'died': datetime.date(2021, 7, 9)
    }

    movieP = {
        'title': 'The Terminal',
        'tmdbld': 594,
        'released': datetime.date(2004, 6, 18),
        'imdbRating': 7.4,
        'movieId': 327,
        'imdbld': 327,
        'year': 2004,
        'runtime': 128,
        'countries': ['USA'],
        'imdbVotes': 399,
        'url': 'https://en.wikipedia.org/wiki/The_Terminal',
        'plot': 'An Eastern European tourist unexpectedly finds himself stranded in JFK airport, and must take up '
                'temporary residence there.',
        'poster': 'https://en.wikipedia.org/wiki/The_Terminal#/media/File:The_Terminal_movie.jpg',
        'budget': 60000000,
        'revenue': 219417255,
        'languages': ['English', 'Bulgarian', 'Spanish', 'Russian', 'French']
    }

    userP = {
        'name': 'Michael Newman',
        'userId': 100
    }

    genreP = {
        'name': 'Comedy'
    }

    createNode(['Person', 'Actor', 'Director'], personActorDirectorProperties, merge=True)
    createNode(['Person', 'Actor'], personActor, merge=True)
    createNode(['Person', 'Director'], personDirector, merge=True)
    createNode(['Movie'], movieP, merge=True)
    createNode(['User'], userP, merge=True)
    createNode(['Genre'], genreP, merge=True)

    createRelationship(NodeD(['Person', 'Actor', 'Director'], personActorDirectorProperties), NodeD(['Movie'], movieP), 'ACTED_IN', {'role': 'Viktor Navorski'})
    createRelationship(NodeD(['Person', 'Actor', 'Director'], personActorDirectorProperties), NodeD(['Movie'], movieP), 'DIRECTED', {'role': 'Director'})
    createRelationship(NodeD(['Person', 'Actor'], personActor), NodeD(['Movie'], movieP), 'ACTED_IN', {'role': 'Alex Goran'})
    createRelationship(NodeD(['Person', 'Director'], personDirector), NodeD(['Movie'], movieP), 'DIRECTED', {'role': 'Director'})
    createRelationship(NodeD(['User'], userP), NodeD(['Movie'], movieP), 'RATED', {'rating': 5, 'timestamp': 1625832000})
    createRelationship(NodeD(['Movie'], movieP), NodeD(['Genre'], genreP), 'IN_GENRE')



# See PyCharm help at https://www.jetbrains.com/help/pycharm/
