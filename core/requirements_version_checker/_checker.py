import sys
import importlib.metadata

from packaging import version
from ._requirements_loader import load_requirements
from packaging.utils import canonicalize_name
from ._modules_list import name_map
from loguru import logger

def check_package_list(strict_mode: bool = False):
    requirements_file = load_requirements()
    for requirement in requirements_file.requirements:
        specifier = requirement.specifier
        if not requirement.name:
            logger.warning(
                f"{requirement.name} has no name"
            )
            continue
        
        try:
            module = name_map[canonicalize_name(requirement.name)]
        except KeyError:
            logger.error(
                "Package {package_name} is not founded.",
                package_name = requirement.name
            )
            continue

        if hasattr(module, "__version__"):
            module_version = module.__version__
        elif requirement.name:
            module_version = importlib.metadata.version(requirement.name)
        else:
            logger.error(
                "Package {package_name} version is not founded.",
                package_name = requirement.name
            )
            continue
        
        if version.parse(module_version) in specifier:
            logger.info(
                "Package {package_name}: {module_version} is ready.",
                package_name = requirement.name,
                module_version = module_version
            )
        else:
            if strict_mode:
                logger.error(
                    "Package {package_name}: {module_version} is not compatible with {requirements}.",
                    package_name = requirement.name,
                    module_version = module_version,
                    requirements = specifier
                )
                sys.exit(1)
            else:
                logger.warning(
                    "The version of Package {package_name} may not be what you want.",
                    package_name = requirement.name
                )
                logger.warning(
                    "{package_name}: {module_version} -/-> {specifier}",
                    package_name = requirement.name,
                    module_version = module_version,
                    specifier = requirement.specifier
                )
    