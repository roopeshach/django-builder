def generate_index_html_content():
    # Create the content for the index.html file with Bootstrap cards
    index_html_content = """
    <!DOCTYPE html>
    <html>
    <!-- Font Awesome -->
<link
  href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
  rel="stylesheet"
/>
<!-- Google Fonts -->
<link
  href="https://fonts.googleapis.com/css?family=Roboto:300,400,500,700&display=swap"
  rel="stylesheet"
/>
<!-- MDB -->
<link
  href="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/7.0.0/mdb.min.css"
  rel="stylesheet"
/>
      <!--Main Navigation-->
  <header>
    <style>
      #intro {
        background-image: url("https://www.yotta.com/wp-content/uploads/2020/10/High-Performance-Computing-to-drive-AI-ML-workloads.jpg");
        height: 110vh;
      }

      /* Height for devices larger than 576px */
      @media (min-width: 992px) {
        #intro {
          margin-top: -58.59px;
        }
      }

      .navbar .nav-link {
        color: #fff !important;
      }
    </style>

    
    <!-- Background image -->
    <div id="intro" class="bg-image shadow-2-strong">
      <div class="mask" style="background-color: rgba(0, 0, 0, 0.8);">
        <div class="container d-flex align-items-center justify-content-center text-center h-100">
          <div class="text-white">
            <h1 class="mb-3">Django App Builder</h1>
            <h5 class="mb-4">Design Your Apps in seconds.</h5>
            <a class="btn btn-outline-primary btn-lg m-2" href="/docs" role="button"
              rel="nofollow" target="_blank">Swagger Docs</a>
            <a class="btn btn-outline-success btn-lg m-2" href="/schema" target="_blank"
              role="button">Build Now</a>
          </div>
        </div>
      </div>
    </div>
    <!-- Background image -->
  </header>
  <!--Main Navigation-->
   <!--Footer-->
  <footer class="bg-light text-lg-start">
  

   
    <!-- Copyright -->
    <div class="text-center p-3" style="background-color: rgba(0, 0, 0, 0.2);">
      © 2020 Copyright:
      <a class="text-dark" href="https://reev-it.com/">Reev InfoTech</a>
    </div>
    <!-- Copyright -->
  </footer>
<!-- MDB -->
<script
  type="text/javascript"
  src="https://cdnjs.cloudflare.com/ajax/libs/mdb-ui-kit/7.0.0/mdb.umd.min.js"
></script>
  
    """
    return index_html_content