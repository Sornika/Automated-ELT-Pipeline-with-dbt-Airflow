{% set film_title = 'Dunkir' %} --Dunkir is the name of the movie

SELECT * FROM {{ ref('films') }} WHERE title = '{{ film_title }}'
