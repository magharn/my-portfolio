import boto3
import io
import zipfile
import mimetypes

def lambda_handler(event, context):
    sns = boto3.resource('sns')
    topic = sns.Topic('arn:aws:sns:us-west-2:647579903866:portfolio-deployPortfolio-topic')

    try:
        s3 = boto3.resource('s3')
        portfolio_bucket = s3.Bucket('portfolio.sergiogtz.info')
        build_bucket = s3.Bucket('portfoliobuild.sergiogtz.info')

        portfolio_zip = io.BytesIO()

        build_bucket.download_fileobj('portfoliobuild.zip', portfolio_zip)

        with zipfile.ZipFile(portfolio_zip) as myzip:
            for nm in myzip.namelist():
                obj = myzip.open(nm)
                portfolio_bucket.upload_fileobj(obj, nm,
                    ExtraArgs={'ContentType' : mimetypes.guess_type(nm)[0]})
                portfolio_bucket.Object(nm).Acl().put(ACL='public-read')

        topic.publish(Subject="Portfolio deployed", Message="Portfolio deployed successfully!.")
    except:
        topic.publish(Subject="Portfolio deploy failed", Message="The portfolio was not deployed successfully!.")
        raise

    return 'portfolio has been deployed!'
