import cloudinary
import cloudinary.uploader


class UploadFileService:
    """
    A service class for uploading files to Cloudinary.

    This class configures Cloudinary with the provided credentials and
    provides a method for uploading files with a unique identifier.
    """

    def __init__(self, cloud_name: str, api_key: str, api_secret: str):
        """
        Initialize the UploadFileService with Cloudinary credentials.

        Args:
            cloud_name (str): The Cloudinary cloud name.
            api_key (str): The Cloudinary API key.
            api_secret (str): The Cloudinary API secret.
        """
        self.cloud_name = cloud_name
        self.api_key = api_key
        self.api_secret = api_secret
        cloudinary.config(
            cloud_name=self.cloud_name,
            api_key=self.api_key,
            api_secret=self.api_secret,
            secure=True,
        )

    @staticmethod
    def upload_file(file, username: str) -> str:
        """
        Upload a file to Cloudinary and return the URL.

        The uploaded file is associated with a public ID that includes
        the specified username. The URL is generated with specific dimensions.

        Args:
            file (File): The file to upload.
            username (str): The username to associate with the file's public ID.

        Returns:
            str: The URL of the uploaded file.
        """
        public_id = f"RestApp/{username}"
        r = cloudinary.uploader.upload(file.file, public_id=public_id, overwrite=True)
        src_url = cloudinary.CloudinaryImage(public_id).build_url(
            width=250, height=250, crop="fill", version=r.get("version")
        )
        return src_url
