@app.route('/routine')
def routine():
    items = load_json(ROUTINE_FILE)
    return render_template('routine.html', routine_items=items)
