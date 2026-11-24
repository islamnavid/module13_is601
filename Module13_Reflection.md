# Module 13 Assignment Reflection

**Student Name:** Md Navidul Islam  
**Course:** IS601 — Python for Web API Development  
**Institution:** New Jersey Institute of Technology  
**Assignment:** Module 13 — JWT Login/Registration with Client-Side Validation & Playwright E2E

## Reflection

In Module 13, I extended my FastAPI Calculations Application by implementing JWT-based user authentication, integrating frontend registration and login pages, and adding automated end-to-end testing using Playwright. I also maintained a GitHub Actions CI/CD pipeline to automate testing, security scanning, and Docker Hub deployment.

One of the most important parts of this assignment was understanding how frontend authentication interacts with backend API endpoints. I implemented registration and login functionality with input validation, password hashing, and JWT authentication. I also worked with frontend forms to display meaningful messages when users entered invalid information, such as an incorrect password or a password that did not meet the minimum requirements.

A significant challenge occurred during Playwright testing. Although the application worked during earlier development, the automated browser tests initially failed because the registration page returned an HTTP 500 error. After investigating the application logs, I identified an issue with the Jinja2 template response implementation. Correcting the template rendering allowed the frontend pages to load properly during automated testing.

Another challenge involved the Trivy security scanner in the GitHub Actions pipeline. Trivy repeatedly reported a vulnerability associated with an outdated setuptools version, even though a newer version was installed in the Docker image. I investigated the installed package versions, Docker image contents, and Trivy scan results. The issue was resolved by updating the Dockerfile to remove bundled pip metadata responsible for the outdated vulnerability detection.

After resolving these issues, the GitHub Actions workflow completed successfully. The testing, security scanning, and deployment jobs all passed, confirming that the automated pipeline could execute its configured checks and publish the Docker image.

This assignment strengthened my understanding of JWT authentication, frontend and backend integration, automated browser testing, debugging, Docker security, and continuous integration and deployment. It also demonstrated the importance of using automated tests and detailed logs to identify problems that may not be immediately visible during manual testing.

Overall, Module 13 provided valuable practical experience in building and testing a more secure, user-focused web application. These skills will be useful when developing larger applications that require authentication, database integration, automated testing, and reliable deployment.
