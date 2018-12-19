import bibtexparser
import markdown

def parse_time_mark( time_mark ):
    first_try = "/".join( [ time_mark[ "day" ], time_mark[ "month" ], time_mark[ "year" ] ] )
    if first_try[ 0 ] == '/':
        first_try = first_try[ 1: ]

    if first_try[ 0 ] == '/':
        first_try = first_try[ 1: ]

    if len( first_try ) == 0:
        first_try = "Future"
    return first_try

def time_mark_to_tuple( time_mark ):
    t = [ 3000, 3000, 3000 ]
    if time_mark[ "day" ] != "":
        t[ 0 ] = int( time_mark[ "day" ] )
    if time_mark[ "month" ] != "":
        t[ 1 ] = int( time_mark[ "month" ] )
    if time_mark[ "year" ] != "":
        t[ 2 ] = int( time_mark[ "year" ] )
        
    return tuple( t[ :: -1 ] )

def parse_title( parsing_method, content_path ):

    if parsing_method == 'bibtex':
        with open( content_path, 'r' ) as bibtex_file:
            bib_database = bibtexparser.load(bibtex_file)

        #print( to_return )
        return bib_database.entries[ 0 ]
    else:
        raise NotImplementedError

def get_body_content( parsing_method, content_path ):

    if parsing_method == 'md':
        with open( content_path, 'r' ) as md_file:
            return markdown.markdown( md_file.read() )
    else:
        raise NotImplementedError

def get_raw_bib( content_path ):
    with open( content_path, 'r' ) as f:
        return f.read()