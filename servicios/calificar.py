def calcular_nota(preguntas, respuestas):
    """Cada pregunta contiene id, puntaje y correcta; respuestas: pregunta -> opción."""
    return sum(p['puntaje'] for p in preguntas if respuestas.get(p['id']) is not None and respuestas.get(p['id']) == p['correcta'])
