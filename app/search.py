import os # type: ignore
from whoosh import index as whoosh_index # type: ignore
from whoosh.fields import Schema, TEXT, ID # type: ignore
from whoosh.qparser import MultifieldParser, OrGroup # type: ignore

WHOOSH_INDEX_DIR = os.path.join(os.path.abspath(os.path.dirname(__file__)), # type: ignore
                                '..', 'whoosh_index')


def _get_schema(searchable_fields):
    fields = {'id': ID(stored=True, unique=True)}
    for field in searchable_fields:
        fields[field] = TEXT(stored=True)
    return Schema(**fields)


def _get_index(index_name, searchable_fields):
    path = os.path.join(WHOOSH_INDEX_DIR, index_name) # type: ignore
    if not os.path.exists(path): # type: ignore
        os.makedirs(path) # type: ignore
        return whoosh_index.create_in(path, _get_schema(searchable_fields))
    if whoosh_index.exists_in(path):
        return whoosh_index.open_dir(path)
    return whoosh_index.create_in(path, _get_schema(searchable_fields))


def add_to_index(index_name, model):
    try:
        ix = _get_index(index_name, model.__searchable__)
        writer = ix.writer()
        attrs = {'id': str(model.id)}
        for field in model.__searchable__:
            attrs[field] = getattr(model, field) or ''
        writer.update_document(**attrs)
        writer.commit()
    except Exception:
        pass


def remove_from_index(index_name, model):
    try:
        path = os.path.join(WHOOSH_INDEX_DIR, index_name)
        if whoosh_index.exists_in(path):
            ix = whoosh_index.open_dir(path)
            writer = ix.writer()
            writer.delete_by_term('id', str(model.id))
            writer.commit()
    except Exception:
        pass


def query_index(index_name, query_string, page, per_page):
    path = os.path.join(WHOOSH_INDEX_DIR, index_name) # type: ignore
    if not os.path.exists(path) or not whoosh_index.exists_in(path): # type: ignore
        return [], 0
    try:
        ix = whoosh_index.open_dir(path)
        with ix.searcher() as searcher:
            text_fields = [f for f in ix.schema.names() if f != 'id']
            if not text_fields:
                return [], 0
            parser = MultifieldParser(text_fields, ix.schema, group=OrGroup)
            q = parser.parse(query_string)
            results = searcher.search(q, limit=None)
            total = len(results)
            start = (page - 1) * per_page
            end = start + per_page
            ids = [int(r['id']) for r in results[start:end]]
        return ids, total
    except Exception:
        return [], 0
