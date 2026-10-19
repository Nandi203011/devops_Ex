# Exercise 9: Jenkins Multi-Stage Pipeline - Deploying a Python Application

## Problem Statement

Automate the CI/CD pipeline for a Python Flask application using a Jenkins **Declarative Pipeline** with the following stages:

1. **Build:** Create a Python virtual environment and install application dependencies.
2. **Test:** Execute unit tests to verify the Flask application.
3. **Deploy:** Copy the application to a mock deployment directory.
4. **Run Application:** Start the deployed Flask application in the background.
5. **Test Application:** Run the test script again to verify application functionality.

**Environment:** Windows, PowerShell terminal, Docker Desktop, Jenkins running inside Docker, Git and GitHub.

---

## Setup Notes

- Jenkins runs inside a Docker container using the `jenkins/jenkins:lts` image.
- Jenkins is accessible through `http://localhost:8080`, as the container maps host port `8080` to container port `8080`.
- The project files are stored in the `Exercise-9` subdirectory of the GitHub repository: [devops_Ex](https://github.com/Nandi203011/devops_Ex).
- The Jenkins job is named `Flask-Multi-Stage-Pipeline`.
- The Jenkinsfile is located at `Exercise-9/Jenkinsfile`.
- Since the project is inside a subdirectory, the pipeline uses `dir('Exercise-9')` for build and test operations.
- Python dependencies are installed inside a virtual environment (`.venv`) within the Jenkins workspace.

---

## Solution (Brief)

1. Start Jenkins using Docker Desktop.
2. Verify that Python 3 is available inside the Jenkins container.
3. Create the Flask application, dependency file, unit test, and Jenkinsfile.
4. Push the files to the GitHub repository.
5. Configure a Jenkins Pipeline job using **Pipeline script from SCM**.
6. Run the pipeline and verify the Build, Test, Deploy, Run Application, and Test Application stages.
7. Confirm that Jenkins reports `Finished: SUCCESS`.

---

## Files Created (in the `Exercise-9` folder)

```text
Exercise-9/
├── app.py
├── requirements.txt
├── test_app.py
├── Jenkinsfile
└── README.md
```

### 1. `app.py`

```python
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return "Hello, Jenkins Multi-Stage Pipeline!"

if __name__ == "__main__":
    app.run(debug=True)
```

### 2. `requirements.txt`

```text
flask==3.1.1
```

### 3. `test_app.py`

```python
import unittest
from app import app

class TestApp(unittest.TestCase):
    def test_home(self):
        tester = app.test_client()
        response = tester.get("/")
        print(response.data.decode("utf-8"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.data.decode("utf-8"),
            "Hello, Jenkins Multi-Stage Pipeline!"
        )

if __name__ == "__main__":
    unittest.main()
```

### 4. `Jenkinsfile`

```groovy
pipeline {
    agent any

    stages {
        stage('Build') {
            steps {
                dir('Exercise-9') {
                    echo 'Creating virtual environment and installing dependencies...'
                    sh 'python3 -m venv .venv'
                    sh '.venv/bin/python -m pip install -r requirements.txt'
                }
            }
        }

        stage('Test') {
            steps {
                dir('Exercise-9') {
                    echo 'Running tests...'
                    sh ".venv/bin/python -m unittest discover -s . -p 'test*.py' -v"
                }
            }
        }

        stage('Deploy') {
            steps {
                echo 'Deploying application...'
                sh '''
                    mkdir -p "${WORKSPACE}/python-app-deploy"
                    cp "${WORKSPACE}/Exercise-9/app.py" "${WORKSPACE}/python-app-deploy/"
                '''
            }
        }

        stage('Run Application') {
            steps {
                echo 'Running application...'
                sh '''
                    nohup "${WORKSPACE}/Exercise-9/.venv/bin/python" \
                    "${WORKSPACE}/python-app-deploy/app.py" \
                    > "${WORKSPACE}/python-app-deploy/app.log" 2>&1 &
                    echo $! > "${WORKSPACE}/python-app-deploy/app.pid"
                '''
            }
        }

        stage('Test Application') {
            steps {
                dir('Exercise-9') {
                    echo 'Testing application...'
                    sh '.venv/bin/python test_app.py'
                }
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }
        failure {
            echo 'Pipeline failed. Check the logs for more details.'
        }
    }
}
```

---

## Commands Executed and Output

### Step 1: Verify that Jenkins is running

Execute the following command in PowerShell:

```powershell
docker ps
```

**Output:**

```text
CONTAINER ID   IMAGE             COMMAND                  CREATED       STATUS        PORTS
59c12ecbc9a0   jenkins/jenkins   "/usr/bin/tini -- /u…"  4 days ago    Up 2 hours    0.0.0.0:8080->8080/tcp
```

The Jenkins container was running successfully, with port `8080` exposed on the host.

Open the Jenkins dashboard at:

http://localhost:8080

### Step 2: Verify Python availability

The Jenkins pipeline requires Python 3, pip, and virtual environment support.

Check the Python version from the Jenkins container:

```powershell
docker exec -it -u root 59c12ecbc9a0 bash
```

Inside the container, install the required packages if they are missing:

```bash
apt-get update
apt-get install -y python3 python3-pip python3-venv
```

Verify Python:

```bash
python3 --version
```

The actual pipeline output confirms that Python and pip were available because the virtual environment was created and Flask was installed successfully.

### Step 3: Push the application to GitHub

From the repository root, add and push the Exercise 9 files:

```powershell
git add Exercise-9
git commit -m "Update Jenkins multi-stage pipeline"
git push origin main
```

The Jenkins console confirmed that the repository was fetched successfully:

```text
Obtained Exercise-9/Jenkinsfile from git https://github.com/Nandi203011/devops_Ex.git
Fetching upstream changes from https://github.com/Nandi203011/devops_Ex.git
Checking out Revision d53e5eeab0507f017a726ca68bd0babfaadde4e1
Commit message: "fixed jenkins"
```

### Step 4: Create the Jenkins Pipeline job

1. Open the Jenkins dashboard.
2. Click **New Item**.
3. Enter `Flask-Multi-Stage-Pipeline`.
4. Select **Pipeline** and click **OK**.

### Step 5: Configure the Pipeline job

Under the **Pipeline** section, configure:

- **Definition:** Pipeline script from SCM
- **SCM:** Git
- **Repository URL:** `https://github.com/Nandi203011/devops_Ex.git`
- **Credentials:** None for a public repository
- **Branch Specifier:** `*/main`
- **Script Path:** `Exercise-9/Jenkinsfile`

Click **Save**.



## Step 6: Execute the Jenkins Pipeline

Click **Build Now** in Jenkins. Open the latest build and select **Console Output** to view the pipeline execution.

### Actual Console Output

```text
Started by user admin

Obtained Exercise-9/Jenkinsfile from git https://github.com/Nandi203011/devops_Ex.git
[Pipeline] Start of Pipeline
[Pipeline] node
Running on Jenkins
 in /var/jenkins_home/workspace/Flask-Multi-Stage-Pipeline
[Pipeline] {
[Pipeline] stage
[Pipeline] { (Declarative: Checkout SCM)
[Pipeline] checkout
Selected Git installation does not exist. Using Default
The recommended git tool is: NONE
No credentials specified
 > git rev-parse --resolve-git-dir /var/jenkins_home/workspace/Flask-Multi-Stage-Pipeline/.git # timeout=10
Fetching changes from the remote Git repository
 > git config remote.origin.url https://github.com/Nandi203011/devops_Ex.git # timeout=10
Fetching upstream changes from https://github.com/Nandi203011/devops_Ex.git
 > git --version # timeout=10
 > git --version # 'git version 2.47.3'
 > git fetch --tags --force --progress -- https://github.com/Nandi203011/devops_Ex.git +refs/heads/*:refs/remotes/origin/* # timeout=10
 > git rev-parse refs/remotes/origin/main^{commit} # timeout=10
Checking out Revision d53e5eeab0507f017a726ca68bd0babfaadde4e1 (refs/remotes/origin/main)
 > git config core.sparsecheckout # timeout=10
 > git checkout -f d53e5eeab0507f017a726ca68bd0babfaadde4e1 # timeout=10
Commit message: "fixed jenkins"
 > git rev-list --no-walk 3aa69d004921a214791fb3456b6ac5f84c593c05 # timeout=10
[Pipeline] }
[Pipeline] // stage
[Pipeline] withEnv
[Pipeline] {
[Pipeline] stage
[Pipeline] { (Build)
[Pipeline] dir
Running in /var/jenkins_home/workspace/Flask-Multi-Stage-Pipeline/Exercise-9
[Pipeline] {
[Pipeline] echo
Creating virtual environment and installing dependencies...
[Pipeline] sh
+ python3 -m venv .venv
+ .venv/bin/python -m pip install -r requirements.txt
Collecting flask==3.1.1 (from -r requirements.txt (line 1))
Successfully installed blinker-1.9.0 click-8.5.0 flask-3.1.1 itsdangerous-2.2.0 jinja2-3.1.6 markupsafe-3.0.4 werkzeug-3.1.9
[Pipeline] }
[Pipeline] // dir
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Test)
[Pipeline] dir
Running in /var/jenkins_home/workspace/Flask-Multi-Stage-Pipeline/Exercise-9
[Pipeline] {
[Pipeline] echo
Running tests...
[Pipeline] sh
+ .venv/bin/python -m unittest discover -s . -p test*.py -v
test_home (test_app.TestApp.test_home) ... ok

----------------------------------------------------------------------
Ran 1 test in 0.053s

OK
Hello, Jenkins Multi-Stage Pipeline!
[Pipeline] }
[Pipeline] // dir
[Pipeline] }
[Pipeline] // stage
[Pipeline] stage
[Pipeline] { (Deploy)
[Pipeline] sh
+ mkdir -p /var/jenkins_home/workspace/Flask-Multi-Stage-Pipeline/python-app-deploy
+ cp /var/jenkins_home/workspace/Flask-Multi-Stage-Pipeline/Exercise-9/app.py /var/jenkins_home/workspace/Flask-Multi-Stage-Pipeline/python-app-deploy/
[Pipeline] }
[Pipeline] // stage
[Pipeline] // stage
[Pipeline] { (Run Application)
[Pipeline] echo
Running application...
[Pipeline] sh
+ echo 2676
+ nohup /var/jenkins_home/workspace/Flask-Multi-Stage-Pipeline/Exercise-9/.venv/bin/python /var/jenkins_home/workspace/Flask-Multi-Stage-Pipeline/python-app-deploy/app.py
[Pipeline] }
[Pipeline] // stage
[Pipeline] }
[Pipeline] // stage
[Pipeline] { (Test Application)
[Pipeline] dir
Running in /var/jenkins_home/workspace/Flask-Multi-Stage-Pipeline/Exercise-9
[Pipeline] {
[Pipeline] echo
Testing application...
[Pipeline] sh
+ .venv/bin/python test_app.py
.
----------------------------------------------------------------------
Ran 1 test in 0.021s

OK
Hello, Jenkins Multi-Stage Pipeline!
[Pipeline] }
[Pipeline] // dir
[Pipeline] }
[Pipeline] // stage
[Pipeline] { (Declarative: Post Actions)
[Pipeline] echo
Pipeline completed successfully!
[Pipeline] }
[Pipeline] // stage
[Pipeline] }
[Pipeline] // withEnv
[Pipeline] }
[Pipeline] // node
[Pipeline] End of Pipeline
Finished: SUCCESS
```

### Execution Summary

| Pipeline stage | Result |
|---|---|
| Git checkout | Successful |
| Build | Dependencies installed |
| Test | 1 test passed |
| Deploy | `app.py` copied successfully |
| Run Application | Background launch command executed |
| Test Application | 1 test passed |
| Final status | `SUCCESS` |



---

## Result

The Jenkins Declarative Pipeline for the Python Flask application was executed successfully.

- The source code and Jenkinsfile were retrieved from GitHub.
- Flask and its dependencies were installed in a Python virtual environment.
- The unit test passed during the Test stage.
- The application was copied into the mock deployment directory.
- The application launch command was executed.
- The Test Application stage passed.
- Jenkins displayed `Pipeline completed successfully!` and `Finished: SUCCESS`.

Thus, the exercise demonstrates the automation of the build, test, deployment, and application verification stages of a Python Flask application using Jenkins and Docker.
