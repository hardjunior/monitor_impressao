from setuptools import setup, find_packages

setup(
    name="monitor_impressao",
    version="1.0.0",
    description="Monitoramento de PDFs para impressão automática com ações pós-processamento",
    author="Ivamar Júnior",
    packages=find_packages(),
    install_requires=[
        "watchdog>=3.0.0",
    ],
    entry_points={
        "console_scripts": [
            "monitor-impressao=monitor_impressao.monitor_impressao:main"
        ]
    },
    include_package_data=True,
    zip_safe=False,
)
