from quart import Blueprint, render_template_string, static
from pathlib import Path

bp = Blueprint('index', __name__)


@bp.route('/<path:path>')
async def static_pages(path):
    """Map requests from / to /static."""
    if '..' in path:
        return 'no', 404

    return await static.send_from_directory('static', path)


@bp.route('/')
@bp.route('/api')
@bp.route('/api/v1')
async def index_handler():
    """Handler for the index page."""
    index_path = Path.cwd() / Path('static') / 'index.html'
    return await render_template_string(index_path.read_text())
