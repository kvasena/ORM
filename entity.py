import sys
import psycopg2
import psycopg2.extras


class DatabaseError(Exception):
    pass


class DataIsNotSaveError(Exception):
    print


class InvalidPropertyName(Exception):
    pass


class RuntimeException(Exception):
    pass


class Entity(object):
    db = None

    # ORM part 1
    __delete_query = 'DELETE FROM "{table}" WHERE {table}_id=%s'
    __insert_query = 'INSERT INTO "{table}" ({columns}) VALUES ({placeholders}) RETURNING "{table}_id"'
    __list_query = 'SELECT * FROM "{table}"'
    __select_query = 'SELECT * FROM "{table}" WHERE {table}_id=%s'
    __update_query = 'UPDATE "{table}" SET {columns} WHERE {table}_id=%s'

    # ORM part 2
    __parent_query = 'SELECT * FROM "{table}" WHERE {parent}_id=%s'
    __sibling_query = 'SELECT * FROM "{sibling}" NATURAL JOIN "{join_table}" WHERE {table}_id=%s'
    __update_children = 'UPDATE "{table}" SET {parent}_id=%s WHERE {table}_id IN ({children})'

    def __init__(self, id=None):
        if self.__class__.db is None:
            raise DatabaseError()

        self.__cursor = self.__class__.db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        self.__fields = {}
        self.__id = id
        self.__loaded = False
        self.__modified = False
        self.__table = self.__class__.__name__.lower()

    def __getattr__(self, name):
        if self.__modified:
            raise DataIsNotSaveError()
        self.__load()
        if name in self._parents:
            return self._get_parent(name)
        if name in self._children.keys():
            return self._get_children(self._children[name])
        if name in self._siblings.keys():
            return self._get_siblings(self._siblings[name])
        return self._get_column(name)

    def __setattr__(self, name, value):
        if name in self._columns:
            self._set_column(name, value)
        else:
            super(Entity, self).__setattr__(name, value)

    def __execute_query(self, query, args):
        try:
            self.__cursor.execute(query, args)
        except Exception as e:
            self.__class__.db.rollback()
            sys.stderr.write(str(e) + '\n')
        else:
            self.__class__.db.commit()

    def __insert(self):
        query = self.__insert_query.format(
                table=self.__table,
                columns=', '.join(self.__fields.keys()),
                placeholders=', '.join(['%s'] * len(self.__fields.keys()))
        )
        self.__execute_query(query, self.__fields.values())
        self.__id = self.__cursor.fetchone()['{table}_id'.format(table=self.__table)]

    def __load(self):
        if self.__id is None or self.__loaded is True:
            return
        query = self.__select_query.format(table=self.__table)
        self.__execute_query(query, (self.__id,))
        self.__fields = self.__cursor.fetchone()

        self.__loaded = True

    def __update(self):
        columns_list = ["{key} = '{value}'".format(key=key, value=value)
                        for key, value in self.__fields.items()]
        columns = ', '.join(columns_list)
        query = self.__update_query.format(table=self.__table, columns=columns)
        self.__execute_query(query, (self.__id,))

    def _get_children(self, name):
        import models

        query = self.__parent_query.format(table=name.lower(), parent=self.__table)
        self.__execute_query(query, (self.__id, ))

        for row in self.__cursor:
            children_id = row['{table}_id'.format(table=name.lower())]
            class_name = name[0].upper() + name[1:]
            cls = getattr(models, class_name)
            instance = cls(children_id)
            instance.__fields = row
            instance.__loaded = True
            yield instance

    def _get_column(self, name):
        field_name = '{table}_{name}'.format(table=self.__table, name=name)

        if field_name not in self.__fields.keys():
            raise InvalidPropertyName()

        return self.__fields[field_name]

    def _get_parent(self, name):
        import models

        parent_id = self.__fields["{name}_id".format(name=name)]
        query = self.__parent_query.format(table=self.__table, parent=name)
        self.__execute_query(query, (parent_id, ))
        class_name = name[0].upper() + name[1:]
        cls = getattr(models, class_name)
        instance = cls(parent_id)

        return instance

    def _get_siblings(self, name):
        import models

        join_table = '{table1}_{table2}'.format(table1=name.lower(), table2=self.__table)
        query = self.__sibling_query.format(sibling=name.lower(), join_table=join_table, table=self.__table)
        self.__execute_query(query, (self.__id, ))
        for row in self.__cursor:
            sibling_id = row['{table}_id'.format(table=name.lower())]
            cls = getattr(models, name)
            instance = cls(sibling_id)
            instance.__fields = row
            instance.__loaded = True
            yield instance

    def _set_column(self, name, value):
        self.__fields['{table}_{name}'.format(table=self.__table, name=name)] = value
        self.__modified = True

    def _set_parent(self, name, value):
        column_name = '{parent}_id'.format(parent=name)
        if isinstance(value, Entity):
            value = value.__id
        self.__fields[column_name] = value

    @classmethod
    def all(cls):
        query = cls.__list_query.format(table=cls.__name__.lower())
        cursor = cls.db.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        cursor.execute(query)
        for row in cursor:
            table_id = row['{table}_id'.format(table=cls.__name__.lower())]
            instance = cls(table_id)
            instance.__fields = row
            instance.__loaded = True
            yield instance

    def delete(self):
        if self.__id is None:
            raise RuntimeException()
        query = self.__delete_query.format(table=self.__table)
        self.__execute_query(query, (self.__id,))

    @property
    def id(self):
        return self.__id

    @property
    def created(self):
        return self.__fields['{table}_created'.format(table=self.__table)]

    @property
    def updated(self):
        return self.__fields['{table}_updated'.format(table=self.__table)]

    def save(self):
        if self.__id is None:
            self.__insert()
        else:
            self.__update()
        self.__modified = False
