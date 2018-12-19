import os, json, time
from datetime import datetime
import pprint

from flask import Flask
from config import Config
from flask import Markup

from flask_bootstrap import Bootstrap

from .tl_parsing import parse_title, get_raw_bib, get_body_content, parse_time_mark, time_mark_to_tuple

app = Flask(__name__)
app.config.from_object(Config)

bootstrap = Bootstrap(app)

pp = pprint.PrettyPrinter(width=41, compact=True)

def db_scan():

    available_lists = []
    uuid_to_id = {}

    for file in os.listdir( Config.TL_DB_PATH  ):
        file_path = os.path.join( Config.TL_DB_PATH, file )
        if file[ 0 ] != '.' and os.path.isdir( file_path ):
            with open( os.path.join( file_path, 'main.json' ), 'r' ) as f:
                main_d = json.load( f )
            main_d['entries'] = []
            available_lists.append( main_d )

    for list_d in available_lists:
        entries_path = os.path.join( Config.TL_DB_PATH, list_d['uuid'], 'entries' )
        for file in os.listdir( entries_path ):
            entry_path = os.path.join( entries_path , file )
            if file[ 0 ] != '.' and os.path.isdir( entry_path ):
                with open( os.path.join( entry_path, 'main.json' ), 'r' ) as f:
                    main_d = json.load( f )
                list_d['entries'].append( main_d )

    available_lists.sort( key = lambda x: float( x["creation_ts"] ) )
    for i in range( len( available_lists ) ):
        uuid_to_id[ available_lists[ i ]['uuid'] ] = i

    for list_d in available_lists:
        entries_path = os.path.join( Config.TL_DB_PATH, list_d['uuid'], 'entries' )
        for entry_d in list_d[ 'entries' ]:
            entry_path = os.path.join( entries_path , entry_d['uuid'] )
            #pp.pprint( entry_d )

            ts_lastmodified = int( os.stat( entry_path ).st_mtime )
            entry_d[ 'last_modified' ] = datetime.fromtimestamp( ts_lastmodified ).isoformat()

            entry_d[ 'time_mark' ][ 'parsed' ] = parse_time_mark( entry_d[ 'time_mark' ] )

            entry_d[ 'title' ][ 'parsed' ] = parse_title( entry_d[ 'title' ]['parsing_method'], os.path.join( entry_path, entry_d['title']['content'] ) )
            entry_d['body'][ 'parsed' ] = Markup( get_body_content( entry_d[ 'body' ]['parsing_method'], os.path.join( entry_path, entry_d['body']['content'] ) ) )
            entry_d[ 'raw_bibtex' ] = get_raw_bib( os.path.join( entry_path, entry_d['title']['content'] ) )

        list_d[ 'entries' ].sort( key = lambda x: time_mark_to_tuple( x[ 'time_mark' ] ) )
        list_d[ 'entries' ] = list_d[ 'entries' ][ :: -1 ]

    return available_lists, uuid_to_id
available_lists, lists_uuid_to_id = db_scan()



from app import routes
