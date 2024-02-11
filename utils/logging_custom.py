import logging

class LogHandler:

    def __init__(
        self, 
        log_to_file: bool = False, 
        log_file_path: str = r"logs\test_output.log"
    ):
        """
        Class able to log statements to console and also to file if specified.

        Arguments:
            log_to_file: Whether to log statements to file
            log_file_path: File to log statements to (statements get appended)
        """

        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.INFO)

        # Create console handler for logging to stdout
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_format = logging.Formatter('%(message)s')
        console_handler.setFormatter(console_format)

        # Add console handler by default
        self.logger.addHandler(console_handler)

        # Create file handler for logging to a file, if requested
        if log_to_file:
            file_handler = logging.FileHandler(log_file_path)
            file_handler.setLevel(logging.INFO)
            file_format = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
            file_handler.setFormatter(file_format)
            self.logger.addHandler(file_handler)

    def example_log(self):
        self.logger.info("This is an example log to test functionality.\n")

    def log(self, string):
        self.logger.info(string)


if __name__ == "__main__":
    lh = LogHandler(
        log_to_file=True,
        log_file_path=r"logs\test_output_manual.log"
    )
    lh.example_log()
    lh.log("Now we test manual logging\n")