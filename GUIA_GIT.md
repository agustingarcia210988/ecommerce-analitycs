# Guía rápida de Git

## Comandos básicos que vas a necesitar:

### Ver el estado de tus archivos
```bash
git status
```

### Agregar archivos al staging (preparar para commit)
```bash
# Agregar un archivo específico
git add extraer_ordenes.py

# Agregar todos los archivos modificados
git add .
```

### Hacer un commit (guardar cambios)
```bash
git commit -m "Descripción de lo que cambiaste"
```

### Ver el historial de commits
```bash
git log
# o más resumido:
git log --oneline
```

### Ver qué cambiaste en los archivos
```bash
git diff
```

## Ejemplo de flujo de trabajo:

1. Modificás archivos
2. Verificás qué cambió: `git status`
3. Agregás los cambios: `git add .`
4. Guardás los cambios: `git commit -m "Agrego filtro de órdenes finalizadas"`
5. Verificás que se guardó: `git log --oneline`

## Estados actuales del proyecto:

Ya tenés 2 commits hechos:
- Primer commit: script básico de extracción
- Agrego tests básicos

Los nuevos cambios (parquet y filtro) todavía no están commiteados.
