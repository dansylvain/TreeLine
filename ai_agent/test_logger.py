from agent.logger import TreeLineLogger

def test_logger():
    logger = TreeLineLogger(log_to_console=True).logger
    
    logger.info("INFO: Logger test - informational message")
    logger.warning("WARNING: Logger test - warning message")
    logger.error("ERROR: Logger test - error message")

    print("Logger test finished. Check the logs/treeline.log file and the console.")

if __name__ == "__main__":
    test_logger()
