import sys
import os
import requests

from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QLabel,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QFileDialog
)


class ResumeApp(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("AI Resume Screening")
        self.resize(700, 500)

        self.selected_file = None
        self.resume_skills = []

        layout = QVBoxLayout()

        title = QLabel("AI Resume Screening System")
        layout.addWidget(title)

        self.upload_btn = QPushButton("Upload Resume PDF")
        self.upload_btn.clicked.connect(self.upload_resume)
        layout.addWidget(self.upload_btn)

        self.job_input = QTextEdit()
        self.job_input.setPlaceholderText("Paste Job Description Here...")
        layout.addWidget(self.job_input)

        self.analyze_btn = QPushButton("Analyze Candidate")
        self.analyze_btn.clicked.connect(self.analyze_candidate)
        layout.addWidget(self.analyze_btn)

        self.result_label = QLabel("Result will appear here")
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def upload_resume(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Resume PDF",
            "",
            "PDF Files (*.pdf)"
        )

        if not file_path:
            return

        self.selected_file = file_path
        filename = os.path.basename(file_path)

        self.result_label.setText("Uploading resume...")

        try:
            with open(file_path, "rb") as pdf_file:
                files = {
                    "file": (filename, pdf_file, "application/pdf")
                }

                response = requests.post(
                    "http://127.0.0.1:8000/upload-resume",
                    files=files
                )

            if response.status_code == 200:
                data = response.json()

                skills = data.get("skills", [])
                self.resume_skills = skills
                skill_text = ", ".join(skills)

                self.result_label.setText(
                    f"Uploaded: {filename}\n"
                    f"Skills: {skill_text}"
                )
            else:
                self.result_label.setText(
                    f"Upload Failed: {response.status_code}"
                )

        except Exception as e:
            self.result_label.setText(f"Error: {str(e)}")

    def analyze_candidate(self):
        if not self.resume_skills:
            self.result_label.setText("Please upload resume first")
            return

        job_description = self.job_input.toPlainText()

        if not job_description.strip():
            self.result_label.setText("Please enter job description")
            return

        payload = {
            "resume_skills": self.resume_skills,
            "job_description": job_description
        }

        try:
            response = requests.post(
                "http://127.0.0.1:8000/match",
                json=payload
            )

            if response.status_code == 200:
                data = response.json()

                score = data["score"]
                matched = ", ".join(data["matched_skills"])
                missing = ", ".join(data["missing_skills"])

                self.result_label.setText(
                    f"Score: {score}%\n"
                    f"Matched: {matched}\n"
                    f"Missing: {missing}"
                )
            else:
                self.result_label.setText(
                    f"Match Failed: {response.status_code}"
                )

        except Exception as e:
            self.result_label.setText(f"Error: {str(e)}")


app = QApplication(sys.argv)
window = ResumeApp()
window.show()
sys.exit(app.exec())