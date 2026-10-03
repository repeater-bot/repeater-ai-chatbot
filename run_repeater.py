import sys
import time
from loguru import logger

def main(run_server: bool = True):
    start_import_time = time.perf_counter_ns()
    try:
        from core import RepeaterMain
    except BaseException as e:
        logger.exception(
            "Import core failed. Please check code and try again. Error: {error_msg}",
            error_msg = str(e),
        )
        input_str = input("Shall we proceed with the program? (y/N)")
        if input_str.lower() in ["y", "yes", "1", "true", "t"]:
            pass
        else:
            sys.exit(1)
    end_import_time = time.perf_counter_ns()

    while True:
        repeater_main = RepeaterMain()

        load_configs_start_time = time.perf_counter_ns()
        configs = repeater_main.load_configs()
        load_configs_end_time = time.perf_counter_ns()

        logger_init_start_time = time.perf_counter_ns()
        repeater_main.init_logger()
        logger_init_end_time = time.perf_counter_ns()

        logger.info(
            "Import Packages Time: {import_packages_time:.2f}ms",
            import_packages_time = (end_import_time - start_import_time) / 1e6
        )
        logger.info(
            "Init Logger Time: {logger_init_time:.2f}ms",
            logger_init_time = (logger_init_end_time - logger_init_start_time) / 1e6
        )
        logger.info(
            "Load Configs Time: {load_configs_time:.2f}ms",
            load_configs_time = (load_configs_end_time - load_configs_start_time) / 1e6
        )

        if run_server is None:
            run_server = configs.server.run_server
        
        repeater_main.init_all(configs)
        repeater_main.init_server(configs)
        repeater_main.set_inited_flag() # Important! The program needs to set this Flag to start.
        
        if run_server:
            exit_code = repeater_main.run()
        
        if exit_code != 0:
            logger.error(
                "Repeater exited with code {exit_code}",
                exit_code = exit_code
            )
            sys.exit(exit_code)
        
        if configs.server.restart:
            logger.info("Repeater Restarting...")
        else:
            break

if __name__ == "__main__":
    main()