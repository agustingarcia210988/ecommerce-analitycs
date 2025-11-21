{% macro extract_date_parts(date_column) %}
    {{ date_column }} as fecha,
    EXTRACT(YEAR FROM {{ date_column }}) as anio,
    EXTRACT(MONTH FROM {{ date_column }}) as mes,
    EXTRACT(DAY FROM {{ date_column }}) as dia,
    EXTRACT(DOW FROM {{ date_column }}) as dia_semana_num,
    CASE EXTRACT(DOW FROM {{ date_column }})
        WHEN 0 THEN 'Domingo'
        WHEN 1 THEN 'Lunes'
        WHEN 2 THEN 'Martes'
        WHEN 3 THEN 'Miercoles'
        WHEN 4 THEN 'Jueves'
        WHEN 5 THEN 'Viernes'
        WHEN 6 THEN 'Sabado'
    END as dia_semana_nombre,
    CASE 
        WHEN EXTRACT(DOW FROM {{ date_column }}) IN (0, 6) THEN 'Fin de semana'
        ELSE 'Dia habil'
    END as tipo_dia,
    EXTRACT(WEEK FROM {{ date_column }}) as semana_anio,
    EXTRACT(QUARTER FROM {{ date_column }}) as trimestre,
    CASE EXTRACT(MONTH FROM {{ date_column }})
        WHEN 1 THEN 'Enero'
        WHEN 2 THEN 'Febrero'
        WHEN 3 THEN 'Marzo'
        WHEN 4 THEN 'Abril'
        WHEN 5 THEN 'Mayo'
        WHEN 6 THEN 'Junio'
        WHEN 7 THEN 'Julio'
        WHEN 8 THEN 'Agosto'
        WHEN 9 THEN 'Septiembre'
        WHEN 10 THEN 'Octubre'
        WHEN 11 THEN 'Noviembre'
        WHEN 12 THEN 'Diciembre'
    END as mes_nombre
{% endmacro %}


{% macro generate_surrogate_key(columns) %}
    MD5(CONCAT_WS('|', {% for col in columns %}{{ col }}{% if not loop.last %}, {% endif %}{% endfor %}))
{% endmacro %}