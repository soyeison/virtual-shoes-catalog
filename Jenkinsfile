// Plantilla: reemplaza los TODO según el stack de cada proyecto.
// Flujo: análisis estático -> pruebas (contenedor efímero) -> imágenes -> escaneo Trivy -> prueba de humo.
pipeline {
  agent any
  stages {

    stage('Pruebas backend') {
      // Equivalente al job api-tests de .github/workflows/ci.yml (Python 3.12, pip, pytest + cobertura)
      // Un parámetro por línea: en una sola, Groovy lo lee como image(...).reuseNode(...)
      agent {
        docker {
          image 'python:3.12-slim'
          reuseNode true
        }
      }
      environment {
        // Caché de pip entre builds, como "cache: pip" en GitHub Actions.
        // Queda fuera de virtual-catalog-api/, así que no entra en el contexto de la imagen.
        PIP_CACHE_DIR = "${WORKSPACE}/.pip-cache"
      }
      steps {
        dir('virtual-catalog-api') {
          // venv limpio en cada build: entorno nuevo como en Actions y sin depender
          // del usuario con el que Jenkins arranque el contenedor
          sh 'python -m venv --clear .venv'
          sh '.venv/bin/pip install -r requirements.txt'
          sh '.venv/bin/pytest -v --cov=app --cov-report=term-missing --junitxml=test-results/junit.xml'
        }
      }
      post {
        always {
          // Publica los resultados en la vista del build (no existe en el workflow de Actions)
          junit allowEmptyResults: true, testResults: 'virtual-catalog-api/test-results/*.xml'
        }
      }
    }

    stage('Construir imágenes') {
      steps {
        sh 'docker build -t backend-ci:${BUILD_NUMBER} ./virtual-catalog-api'
        sh 'docker build -t frontend-ci:${BUILD_NUMBER} ./shoes-web-app'
      }
    }

    stage('Prueba de humo') {
      // Configuración de la prueba (no son secretos; los secretos se generan en cada build)
      environment {
        S3_BUCKET = 'catalogo-images'
        S3_REGION = 'us-east-1'
        JWT_ALGORITHM = 'HS256'
        JWT_EXPIRATION_MINUTES = '60'
      }
      steps {
        // Comprueba que el build arranca y que sus piezas se conectan:
        // el backend está listo (base de datos + almacenamiento) y el frontend lo consume.
        sh '''
          NET=smoke-${BUILD_NUMBER}
          cleanup() {
            docker rm -f storage-$NET backend-$NET frontend-$NET >/dev/null 2>&1 || true
            docker network rm $NET >/dev/null 2>&1 || true
          }
          trap cleanup EXIT

          fail() {
            echo "Prueba de humo fallida: $1"
            for c in storage backend frontend; do
              echo "--- logs de $c ---"
              docker logs $c-$NET 2>&1 || true
            done
            exit 1
          }

          docker network create $NET

          # Credenciales desechables: el almacenamiento solo vive durante este build.
          # Sin traza (-x) para que sus valores no lleguen al log; a Docker se le pasan
          # las variables solo por nombre (-e VAR), así el valor nunca aparece en un comando.
          set +x
          rand() { head -c "$1" /dev/urandom | od -An -tx1 | tr -d ' \\n'; }
          export S3_ACCESS_KEY=$(rand 10) S3_SECRET_KEY=$(rand 20) JWT_SECRET_KEY=$(rand 32)
          export RUSTFS_ACCESS_KEY=$S3_ACCESS_KEY RUSTFS_SECRET_KEY=$S3_SECRET_KEY
          export AWS_ACCESS_KEY_ID=$S3_ACCESS_KEY AWS_SECRET_ACCESS_KEY=$S3_SECRET_KEY

          # El readiness del backend exige almacenamiento S3 con el bucket creado
          docker run -d --name storage-$NET --network $NET --network-alias storage \
            -e RUSTFS_ACCESS_KEY -e RUSTFS_SECRET_KEY -e RUSTFS_ADDRESS=:9000 \
            rustfs/rustfs:1.0.4

          bucket=0
          for i in $(seq 1 20); do
            if docker run --rm --network $NET \
                 -e AWS_ACCESS_KEY_ID -e AWS_SECRET_ACCESS_KEY -e AWS_DEFAULT_REGION=$S3_REGION \
                 amazon/aws-cli:2.31.0 --endpoint-url http://storage:9000 s3api create-bucket --bucket "$S3_BUCKET"; then
              bucket=1
              break
            fi
            sleep 3
          done
          [ $bucket = 1 ] || fail "no se pudo crear el bucket"

          # El .env no entra en la imagen (.dockerignore): las variables se pasan aquí
          # El alias "backend" es el nombre con el que el frontend encuentra al backend
          docker run -d --name backend-$NET --network $NET --network-alias backend \
            -e DATABASE_PATH=data/catalogo.db \
            -e CORS_ORIGINS='["http://localhost:4321"]' \
            -e S3_ENDPOINT=http://storage:9000 \
            -e S3_PUBLIC_URL=http://storage:9000 \
            -e S3_ACCESS_KEY \
            -e S3_SECRET_KEY \
            -e S3_BUCKET \
            -e S3_REGION \
            -e JWT_SECRET_KEY \
            -e JWT_ALGORITHM \
            -e JWT_EXPIRATION_MINUTES \
            -e PAYMENT_GATEWAY_PROVIDER=mock \
            backend-ci:${BUILD_NUMBER}

          docker run -d --name frontend-$NET --network $NET \
            -e INTERNAL_API_URL=http://backend:8000/api/v1 \
            frontend-ci:${BUILD_NUMBER}

          # 1. Backend listo: responde 200 solo si la base de datos y el almacenamiento están bien
          ready=0
          for i in $(seq 1 20); do
            if docker exec frontend-$NET wget -qO- http://backend:8000/api/v1/health/ready; then
              ready=1
              break
            fi
            sleep 3
          done
          [ $ready = 1 ] || fail "el backend no quedó listo (ver /api/v1/health/ready en sus logs)"

          # 2. Frontend funcionando: la portada se renderiza en el servidor llamando al backend.
          # Si esa llamada falla la página igual responde 200, por eso se busca el mensaje de error.
          # 127.0.0.1 y no localhost: en Alpine localhost resuelve a ::1 y Astro solo escucha en IPv4.
          page=""
          for i in $(seq 1 10); do
            page=$(docker exec frontend-$NET wget -qO- http://127.0.0.1:4321/) && break
            page=""
            sleep 3
          done
          [ -n "$page" ] || fail "el frontend no respondió"
          if echo "$page" | grep -q "No pudimos conectar"; then
            fail "el frontend no pudo obtener el catálogo del backend"
          fi

          echo "Prueba de humo superada"
        '''
      }
    }
  }

  post {
    always {
      sh 'docker image prune -f || true'
    }
  }
}
