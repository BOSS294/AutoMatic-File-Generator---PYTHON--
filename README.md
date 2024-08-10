# Project Directory Creator

## Overview

The **Project Directory Creator** is a Python-based application that allows users to create predefined directory structures for `web development projects`. The tool uses a GUI built with CustomTkinter to provide an intuitive interface for entering project names, selecting a directory, and generating the required folder and file structure with just a few clicks.

## Features

- **CustomTkinter GUI**: A clean and modern interface designed with CustomTkinter, making it easy to use and visually appealing.
- **Progress Feedback**: A progress bar starts in red, turns green upon successful creation of the directory structure, and reverts to red when a new directory is selected.
- **Error Handling**: User-friendly error messages if the project name is not entered or the directory is not selected.
- **Logs Area**: A dedicated section to display logs of all directories and files created during the process.
- **Predefined Structure**: Automatically generates a set of folders and files typical for web development projects.

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/BOSS294/project-directory-creator.git
   cd project-directory-creator
   ```

2. **Install required packages**:
   Make sure you have Python installed. Then, install the required packages:
   ```bash
   pip install customtkinter
   ```

3. **Run the application**:
   ```bash
   python directory_creator.py
   ```

## How to Use

1. **Enter Project Name**: Provide a name for your project in the input field.
2. **Select Directory**: Choose the base directory where the project structure should be created.
3. **Create Structure**: Click the "Create Structure" button to generate the folders and files.
4. **Monitor Progress**: Watch the progress bar and logs area for feedback on the structure creation process.

## Directory Structure

The application creates the following structure:

```
ProjectName/
│
├── Assets/
│   ├── Accounts/
│   │   ├── Contents/
│   │   ├── Pages/
│   │   │   ├── login.php
│   │   │   ├── register.php
│   │   │   └── user-dashboard.php
│   │   ├── Processors/
│   │   ├── Scripts/
│   │   │   └── accounts.js
│   │   └── Styles/
│   ├── Admins/
│   │   ├── Contents/
│   │   ├── Pages/
│   │   │   └── admin-dashboard.php
│   │   ├── Processors/
│   │   ├── Scripts/
│   │   └── Styles/
│   ├── Extras/
│   │   ├── Connections/
│   │   ├── Documentations/
│   │   ├── Helps/
│   │   └── Updates/
│   └── Website/
│       ├── Contents/
│       ├── Images/
│       ├── Pages/
│       │   ├── about-us.php
│       │   ├── contact.php
│       │   ├── faqs.php
│       │   ├── privacy-policy.php
│       │   └── terms-conditions.php
│       ├── Processors/
│       ├── Scripts/
│       │   └── main.js
│       ├── Styles/
│       └── Videos/
└── index.php
```

## How to Contribute?

We welcome contributions from the community! If you would like to contribute to this project, please follow the steps below:

### 1. Fork the Repository

- Navigate to the [Project Directory Creator repository](https://github.com/BOSS294/project-directory-creator) on GitHub.
- Click the "Fork" button in the upper right corner to create a copy of the repository under your GitHub account.

### 2. Clone Your Fork

- Open your terminal or command prompt.
- Clone your forked repository to your local machine:
  ```bash
  git clone https://github.com/yourusername/project-directory-creator.git
  cd project-directory-creator
  ```

### 3. Create a Branch

- Create a new branch to work on your feature or bugfix:
  ```bash
  git checkout -b feature/your-feature-name
  ```
  Replace `your-feature-name` with a descriptive name for your feature or bugfix.

### 4. Make Changes

- Make the necessary changes to the codebase.
- Ensure that your changes are well-documented and include comments where appropriate.
- Test your changes to ensure that they work as expected.

### 5. Commit Your Changes

- Once your changes are ready, stage them for commit:
  ```bash
  git add .
  ```
- Commit your changes with a descriptive commit message:
  ```bash
  git commit -m "Feat: description of your feature"
  ```

### 6. Push to Your Fork

- Push your changes to the branch on your forked repository:
  ```bash
  git push origin feature/your-feature-name
  ```

### 7. Create a Pull Request

- Navigate to the original [Project Directory Creator repository](https://github.com/BOSS294/project-directory-creator) on GitHub.
- Click the "Pull Requests" tab and then click the "New Pull Request" button.
- Select the branch with your changes and create the pull request (PR).
- Provide a detailed description of your changes and why they should be merged.
- Submit your pull request for review.

### 8. Address Feedback

- Be responsive to any feedback or questions from the maintainers.
- Make any necessary revisions by pushing additional commits to your branch.

### 9. Celebrate

- Once your pull request is merged, your contribution will be part of the project! 🎉

## Guidelines

- Write clear, concise commit messages.
- Ensure your code is well-tested and does not introduce any new bugs.
- Be respectful and considerate in all interactions with the reviewers of your PR.
