Flipper App Submission Validator & Builder
The Flipper App Submission Validator & Builder is an indispensable graphical utility crafted to radically simplify and fortify the process of submitting custom applications to the official Flipper Zero App Catalog. It functions as a powerful, automated pre-submission gatekeeper, giving developers the confidence to know their app meets all necessary technical, structural, and dependency requirements before final submission.

Guaranteed Submission Readiness
This application directly tackles the most frequent reasons for application rejection by automating key compliance steps, turning a complex, error-prone command-line process into a clear, guided workflow:

Guided Pathing: The utility starts with two easy steps: asking the user to graphically select the project's root directory and then the specific application manifest file (manifest.yml). This guided approach is crucial for establishing the correct relative path resolution that the Flipper build system demands, eliminating common configuration errors.

Zero-Error Packaging: By wrapping and controlling the execution of the official Flipper build script (bundle.py), the Validator ensures the final package.zip artifact is created only if the structural, manifest, and compiler checks pass successfully (indicated by a zero exit code). The moment you see the success pop-up, you know the package is formatted correctly for the Catalog.

Dependency Auto-Management: A major feature is its ability to self-heal the environment. The tool first verifies the installation of pip (and attempts to install it via ensurepip if missing), then proceeds to automatically install all required Python packages (pyyaml, requests, etc.). This robust dependency check removes the biggest barrier new contributors face.

Real-Time Validation: A dedicated log window displays the entire output from the build process in real-time. This allows developers to instantly see any structural warnings or compiler errors (like the notorious "Invalid appid" or path issues) and fix them quickly.

Format Compliance: The build process enforces all mandatory structural checks, guaranteeing compliance with critical requirements, such as lowercase app IDs and correct file hierarchy, which are non-negotiable for Catalog acceptance.

In short, the Validator transforms the arduous validation and packaging into a simple, confidence-inspiring graphical process, certifying that your application meets the high technical standards required for the Flipper Zero App Catalog.
